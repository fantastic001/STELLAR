// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient/node";

let client: LanguageClient;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "stellar-language-bindings" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	const disposable = vscode.commands.registerCommand('stellar-language-bindings.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from Stellar Language Bindings!');
	});

	context.subscriptions.push(disposable);


		const exec = require('child_process').exec;
			const config = vscode.workspace.getConfiguration('stellarLanguageBindings');
			const stellarPath = config.get<string>('stellarPath', 'stellar');
			exec(`command -v ${stellarPath}`, (err: any, stdout: string) => {
				if (err || !stdout) {
					vscode.window.showErrorMessage(`The command '${stellarPath}' cannot be found in your PATH. Please install Stellar CLI or set the correct path in the extension settings.`);
					return;
				}

				const serverOptions: ServerOptions = {
					command: stellarPath,
					args: ['lsp_stdio'],
					options: {},
				};

				const clientOptions: LanguageClientOptions = {
					documentSelector: [{ scheme: "file", language: "stellar" }],
				};

				client = new LanguageClient(
					"stellar-lsp",
					"Stellar Language Server (stdio)",
					serverOptions,
					clientOptions
				);
				client.start();
			});
}


export function deactivate(): Thenable<void> | undefined {
  return client ? client.stop() : undefined;
}
