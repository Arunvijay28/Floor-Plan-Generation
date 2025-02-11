// Adjacency matrix
const probMatrix = [
  [0, 38.74845347, 37.49560461, 15.05111675, 20.97284626, 23.11519177],
  [48.5993368, 0, 37.66028, 25.7640352, 8.09689486, 41.6360399],
  [39.0916497, 31.3048201, 0, 15.5763747, 12.1004752, 19.6184657],
  [30.52481445, 41.66028367, 30.30030903, 0, 23.37233565, 28.04204855],
  [34.3354228, 10.56884568, 19.00132191, 18.86699928, 0, 51.4221142],
  [23.74765855, 34.10489698, 19.33235215, 14.20524485, 32.26919989, 0],
];

const threshold = 27; // Edge creation threshold
const ROOM_CLASS = {
  "Living Room": 1, "Kitchen": 2, "MasterRoom": 3, "Bathroom": 4, "Balcony": 5, "entrance": 6, 
  "dining room": 7, "CommonRoom": 8, "storage": 10, "front door": 15, "unknown": 16, "interior_door": 17
};

// Room types and their colors
const roomOptions = {
  "entrance": "#BFE3E8",
  "dining room": "#7BA779",
  // "CommonRoom": "#E87A90",
  "storage": "#FF8C69",
  "front door": "#1F849B",
  "unknown": "#727171",
  "interior_door": "#D3A2C7"
};

// Generate nodes and edges
const nodes = [];
const edges = [];
const nodedata=[];
const numNodes = probMatrix.length;
const initial_rooms = ['Living Room', 'Bathroom', 'Kitchen', 'CommonRoom', 'Balcony', 'MasterRoom'];
const colors = ["#eee8aa", "#ffd700", "#add8e6", "#ffa500", "#6b8e23", "#f08080"];

for (let i = 0; i < numNodes; i++) {
  const roomName = initial_rooms[i];
  const roomId = ROOM_CLASS[roomName] - 1;

  nodes.push({
    id: roomId,
    label: roomName,
    color: colors[i],
  });

  nodedata.push(roomId);

  for (let j = i + 1; j < numNodes; j++) {
    if (probMatrix[i][j] > threshold) {
      const toRoomId = ROOM_CLASS[initial_rooms[j]] - 1;
      edges.push({ from: roomId, to: toRoomId });
    }
  }
}

console.log("Edges created from probability matrix:", edges);
console.log(nodedata);

const container = document.getElementById("network");
const controls = document.getElementById("controls");
const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };

// Create buttons for each room type
Object.keys(roomOptions).forEach((room) => {
  const button = document.createElement("button");
  button.textContent = room;
  button.style.backgroundColor = roomOptions[room];
  button.addEventListener("click", () => {
    const roomId = ROOM_CLASS[room] - 1;

    if (!ROOM_CLASS[room]) {
      console.error(`ROOM_CLASS does not contain: ${room}`);
      return;
    }

    const newNode = {
      id: roomId,
      label: room,
      color: roomOptions[room],
    };
    nodedata.push(roomId);

    data.nodes.add(newNode);
    nodes.push(newNode);
    console.log("Nodes:", nodes);
    console.log("Edges:", edges);
  });

  controls.appendChild(button);
});

const options = {
  interaction: { hover: true },
  manipulation: {
    enabled: true,
    addEdge: (edgeData, callback) => {
      const fromNode = data.nodes.get(edgeData.from);
      const toNode = data.nodes.get(edgeData.to);

      if (!fromNode || !toNode) {
        console.error("Invalid edge connection.");
        callback(null);
        return;
      }

      edgeData.from = fromNode.id;
      edgeData.to = toNode.id;

      if (confirm("Do you want to connect these nodes?")) {
        callback(edgeData);
        edges.push(edgeData);
        console.log("Edges:", edges);
        console.log("nodes:",nodedata);
      } else {
        callback(null);
      }
    },
    deleteEdge: (edgeData, callback) => {
      if (confirm("Do you want to remove this edge?")) {
        callback(edgeData);
      } else {
        callback(null);
      }
    },
  },
};

const network = new vis.Network(container, data, options);

network.on("click", (params) => {
  console.log("Selected edges:", params.edges);
  console.log("Selected nodes:", params.nodes);
});

// Handle "Generate" button click
document.getElementById("generateButton").addEventListener("click", () => {
console.log("Nodes to send:", nodedata); 
console.log("Edges to send:", edges);

fetch("/layout_retrieval", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        nodes: nodedata, 
        edges: edges
    }),
})
.then(response => response.json())
.then(data => {
    console.log("Response from server:", data);
    if (data.success) {
      
        window.location.href = "/display_images"; // Adjust as needed
    } else {
        alert("Error processing layout retrieval: " + data.error);
    }
})
.catch(error => {
    console.error("Error:", error);
    alert("Failed to process the request.");
});
});

