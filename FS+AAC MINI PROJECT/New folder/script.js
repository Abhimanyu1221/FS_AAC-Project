// Graph with 10 nodes
const graph = {
  1: [2, 3],
  2: [4, 5],
  3: [6, 7],
  4: [8, 9],
  5: [],
  6: [],
  7: [],
  8: [],
  9: [10],
  10: []
};

// Node positions for visualization
const positions = {
  1: { x: 400, y: 50 },
  2: { x: 250, y: 150 },
  3: { x: 550, y: 150 },
  4: { x: 150, y: 250 },
  5: { x: 350, y: 250 },
  6: { x: 500, y: 250 },
  7: { x: 650, y: 250 },
  8: { x: 100, y: 350 },
  9: { x: 200, y: 350 },
  10: { x: 250, y: 450 }
};

// Draw Graph
function drawGraph(ctx, visited = [], current = null) {
  ctx.clearRect(0, 0, 800, 500);

  // Draw edges
  for (let node in graph) {
    graph[node].forEach(neighbor => {
      ctx.beginPath();
      ctx.moveTo(positions[node].x, positions[node].y);
      ctx.lineTo(positions[neighbor].x, positions[neighbor].y);
      ctx.stroke();
    });
  }

  // Draw nodes
  for (let node in positions) {
    ctx.beginPath();
    ctx.arc(positions[node].x, positions[node].y, 25, 0, 2 * Math.PI);

    if (current === parseInt(node)) {
      ctx.fillStyle = "orange"; // current node
    } else if (visited.includes(parseInt(node))) {
      ctx.fillStyle = "lightgreen"; // visited
    } else {
      ctx.fillStyle = "white"; // not visited
    }

    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "black";
    ctx.fillText(node, positions[node].x - 5, positions[node].y + 5);
  }
}

// BFS Visualization
function runBFS() {
  const canvas = document.getElementById("bfsCanvas");
  const ctx = canvas.getContext("2d");
  ctx.font = "16px Arial";

  let visited = [];
  let queue = [1]; // start from node 1

  function bfsStep() {
    if (queue.length === 0) return;

    let node = queue.shift();
    if (!visited.includes(node)) {
      visited.push(node);
      drawGraph(ctx, visited, node);

      setTimeout(() => {
        graph[node].forEach(neighbor => {
          if (!visited.includes(neighbor) && !queue.includes(neighbor)) {
            queue.push(neighbor);
          }
        });
        bfsStep();
      }, 1000);
    }
  }

  bfsStep();
}

// DFS Visualization (recursive with delay)
function runDFS() {
  const canvas = document.getElementById("dfsCanvas");
  const ctx = canvas.getContext("2d");
  ctx.font = "16px Arial";

  let visited = [];
  let order = [];

  function dfs(node) {
    if (visited.includes(node)) return;
    visited.push(node);
    order.push(node);

    setTimeout(() => {
      drawGraph(ctx, visited, node);

      graph[node].forEach(neighbor => {
        dfs(neighbor);  // go deep immediately
      });
    }, order.length * 1000);
  }

  dfs(1); // start DFS from node 1
}
  