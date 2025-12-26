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

from stellar import get_available_functions, get_available_types, partial_parse


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
    print("Text before cursor:", text_before_cursor)
    executor, parsed_text, remaining = partial_parse(text_before_cursor)
    print("Remaining text for completions:", remaining)
    if executor is None:
        print("No executor found")
        return CompletionList(is_incomplete=False, items=[
            CompletionItem(
                kind=CompletionItemKind.Snippet,
                detail="Table Definition",
                documentation="Define a new table",
                label="table ${table_name} {\n\t${column_name}: ${type} as \"${alias}\"\n} from \"${source}\" {\n\t${options}\n}",
            ),
        ])
    else:
        # Here you can analyze `executor`, `parsed_text`, and `remaining` to provide context-aware completions.

        if remaining.strip() == "":
            print("Providing top-level completions")
            items = [
                CompletionItem(
                    label="let",
                    kind=CompletionItemKind.Keyword,
                    detail="Keyword",
                    documentation="Let statement",
                ),
                CompletionItem(
                    label="filter",
                    kind=CompletionItemKind.Keyword,
                    detail="Keyword",
                    documentation="Filter statement",
                ),
                CompletionItem(
                    label="export",
                    kind=CompletionItemKind.Keyword,
                    detail="Keyword",
                    documentation="Export statement",
                ),
                # export statement completions
                CompletionItem(
                    kind=CompletionItemKind.Snippet,
                    detail="Export Statement",
                    documentation="Export data to a target",
                    label="export ${table_name} to \"${target}\" {\n\tgroupby: \"${column}\"\n\toperation: \"${operation}\"\n\ttarget: \"${target_column}\"\n}",
                ),
            ]
            return CompletionList(is_incomplete=False, items=items)
        else:
            if remaining.strip().endswith("let"):
                print("Providing completions for 'let '")
                table = executor.load_table()
                table = executor.apply_filters(table)
                table = executor.apply_transformations(table)
                columns = table.columns
                items = [
                    CompletionItem(
                        label=column,
                        kind=CompletionItemKind.Variable,
                        detail="Column",
                        documentation="",
                    ) for column in columns
                ]
                return CompletionList(is_incomplete=False, items=items)
            elif remaining.strip().endswith("filter"):
                print("Providing completions for 'filter '")
                table = executor.load_table()
                table = executor.apply_filters(table)
                table = executor.apply_transformations(table)
                columns = table.columns
                items = [
                    CompletionItem(
                        label=column,
                        kind=CompletionItemKind.Variable,
                        detail="Column",
                        documentation="",
                    ) for column in columns
                ]
                return CompletionList(is_incomplete=False, items=items)
            else:
                print("Providing completions for '= '")
                table = executor.load_table()
                table = executor.apply_filters(table)
                table = executor.apply_transformations(table)
                columns = table.columns
                items = [
                    CompletionItem(
                        label=column,
                        kind=CompletionItemKind.Variable,
                        detail="Column",
                        documentation="",
                    ) for column in columns
                ]
                functions = get_available_functions() 
                items.extend([
                    CompletionItem(
                        label=f"{func}()",
                        kind=CompletionItemKind.Function,
                        detail="Function",
                        documentation="",
                    ) for func, _ in functions.items()
                ])
                items.append(
                    CompletionItem(
                        label="if",
                        kind=CompletionItemKind.Keyword,
                        detail="Keyword",
                        documentation="If expression",
                    )
                )
                return CompletionList(is_incomplete=False, items=items)
    
    # Either a plain list[CompletionItem] or a CompletionList is acceptable.
    return CompletionList(is_incomplete=False, items=[])


if __name__ == "__main__":
    # Runs an LSP server over TCP at 127.0.0.1:5000
    # VS Code client must connect via socket (not stdio).
    server.start_tcp("127.0.0.1", 5000)
