/* Main-document lifecycle receipts from Chromium's external protocol. */
async function observeNavigation(page) {
  const navigation = {status:'unavailable', events:[]};
  let session, mainFrameId, currentDocument, actionIndex = null, sequence = 0;
  let finished, listening = false;
  const documents = new Map();
  const failed = error => {
    navigation.status = listening ? 'partial' : 'unavailable';
    navigation.error ||= String(error.message || error);
  };
  const record = (kind, document, url) => navigation.events.push({
    kind, document_sequence:document.sequence, url,
    observed_during_action_index:actionIndex,
    committed_during_action_index:document.actionIndex,
  });
  const protect = handler => event => {
    try {handler(event);} catch (error) {failed(error);}
  };
  const committed = protect(({frame}) => {
    if (frame.id !== mainFrameId) return;
    if (!frame.loaderId || typeof frame.url !== 'string')
      throw new Error('Main-document commit lacks loader identity or URL.');
    currentDocument = documents.get(frame.loaderId);
    if (!currentDocument) {
      currentDocument = {sequence:++sequence, loaded:false};
      documents.set(frame.loaderId, currentDocument);
    }
    currentDocument.actionIndex = actionIndex;
    currentDocument.url = frame.url + (frame.urlFragment || '');
    record('main_document_commit', currentDocument, currentDocument.url);
  });
  const loaded = protect(event => {
    if (event.frameId !== mainFrameId || event.name !== 'load') return;
    const document = documents.get(event.loaderId);
    // Enabling lifecycle events can replay the initial about:blank load.
    if (!document && !currentDocument) return;
    if (!document) throw new Error('Main-document load has no recorded commit.');
    if (!document.loaded) {
      document.loaded = true;
      record('main_document_load', document, document.url);
    }
  });
  const withinDocument = protect(event => {
    if (event.frameId !== mainFrameId) return;
    if (!currentDocument) throw new Error('Same-document navigation has no recorded commit.');
    if (typeof event.url !== 'string') throw new Error('Same-document navigation lacks URL.');
    record('same_document_navigation', currentDocument, event.url);
  });
  try {
    session = await page.context().newCDPSession(page);
    const {frameTree} = await session.send('Page.getFrameTree');
    mainFrameId = frameTree.frame.id;
    if (!mainFrameId) throw new Error('Main-frame identity is unavailable.');
    session.on('Page.frameNavigated', committed);
    session.on('Page.lifecycleEvent', loaded);
    session.on('Page.navigatedWithinDocument', withinDocument);
    await session.send('Page.enable');
    await session.send('Page.setLifecycleEventsEnabled', {enabled:true});
    navigation.status = navigation.error ? 'partial' : 'complete';
    listening = true;
  } catch (error) {failed(error);}
  return {
    navigation,
    setActionIndex(index) {actionIndex = index;},
    finish() {
      if (!finished) finished = (async () => {
        if (!session) return;
        // Drain already emitted protocol events before freezing both receipts.
        if (listening) {
          try {
            const {frameTree} = await session.send('Page.getFrameTree');
            const frame = frameTree.frame;
            const initialBlank = !currentDocument && frame.url === 'about:blank';
            const recordedCurrent = currentDocument &&
              documents.get(frame.loaderId) === currentDocument;
            if (frame.id !== mainFrameId || (!initialBlank && !recordedCurrent))
              throw new Error('Current main document has no recorded commit.');
          } catch (error) {failed(error);}
        }
        session.removeListener('Page.frameNavigated', committed);
        session.removeListener('Page.lifecycleEvent', loaded);
        session.removeListener('Page.navigatedWithinDocument', withinDocument);
        try {await session.detach();} catch (error) {failed(error);}
      })();
      return finished;
    },
  };
}
module.exports = {observeNavigation};
