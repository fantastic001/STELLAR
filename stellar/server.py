from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    TEXT_DOCUMENT_COMPLETION,
    INITIALIZE,
)


class MyLanguageServer(LanguageServer):
    pass


server = MyLanguageServer("my-lsp", "0.1.0")

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: MyLanguageServer, params: CompletionParams):
    # You can use params.text_document.uri and params.position to build context-aware items.
    text_before_cursor = ls.workspace.get_text_document(
        params.text_document.uri
    ).source[: ls.workspace.get_text_document(
        params.text_document.uri
    ).offset_at_position(params.position)]
    items = [
        CompletionItem(
            label="select",
            kind=CompletionItemKind.Keyword,
            detail="Keyword",
            documentation="Select statement",
        ),
        CompletionItem(
            label="from",
            kind=CompletionItemKind.Keyword,
            detail="Keyword",
            documentation="From clause",
        ),
        CompletionItem(
            label="where",
            kind=CompletionItemKind.Keyword,
            detail="Keyword",
            documentation="Where clause",
        ),
        CompletionItem(
            label="myFunction()",
            kind=CompletionItemKind.Function,
            detail="Function",
            documentation="Example function completion",
        ),
    ]

    # Either a plain list[CompletionItem] or a CompletionList is acceptable.
    return CompletionList(is_incomplete=False, items=items)


if __name__ == "__main__":
    # Runs an LSP server over TCP at 127.0.0.1:5000
    # VS Code client must connect via socket (not stdio).
    server.start_tcp("127.0.0.1", 5000)
