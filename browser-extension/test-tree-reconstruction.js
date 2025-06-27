// Test the new simple PRE block approach
const testTreeText =
  'tree -L 2 . ├── Dockerfile ├── README-model-runner.md ├── README.md ├── backend.env ├── compose.yaml ├── frontend .. ├── go.mod ├── go.sum ├── grafana │ └── provisioning ├── main.go ├── main_branch_update.md ├── observability │ └── README.md ├── pkg │ ├── health │ ├── logger │ ├── metrics │ ├── middleware │ └── tracing ├── prometheus │ └── prometheus.yml ├── refs │ └── heads .. 21 directories, 33 files';

function simpleTreeFix(text) {
  // If text doesn't have newlines but contains tree characters, manually split on tree symbols
  if (!text.includes('\n') && (text.includes('├──') || text.includes('└──'))) {
    console.log('Manually splitting collapsed tree content');
    return text.replace(/(├──|└──)/g, '\n$1').replace(/^\n/, '');
  }
  return text;
}

console.log('Original text:');
console.log(testTreeText);
console.log('\nFixed:');
console.log(simpleTreeFix(testTreeText));
