import React from 'react';
import './styles/network_graph.scss';
import CytoscapeComponent from 'react-cytoscapejs';
import {getCookie} from "../local/cookie";
import DeviceModal from "./DeviceModal";
import {toast} from "react-toastify";
import {getNetworkConf, saveNetworkConf, testConnection} from "../api/holypot";

const svgIcon = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
    <g transform="scale(.7) translate(100, 100)">
    <path fill="#ffffff"
          d="M5.8 309.7C2 292.7 0 275.5 0 258.3 0 135 99.8 35 223.1 35c16.6 0 33.3 2 49.3 5.5C149 87.5 51.9 186 5.8 309.7zm392.9-189.2C385 103 369 87.8 350.9 75.2c-149.6 44.3-266.3 162.1-309.7 312 12.5 18.1 28 35.6 45.2 49 43.1-151.3 161.2-271.7 312.3-315.7zm15.8 252.7c15.2-25.1 25.4-53.7 29.5-82.8-79.4 42.9-145 110.6-187.6 190.3 30-4.4 58.9-15.3 84.6-31.3 35 13.1 70.9 24.3 107 33.6-9.3-36.5-20.4-74.5-33.5-109.8zm29.7-145.5c-2.6-19.5-7.9-38.7-15.8-56.8C290.5 216.7 182 327.5 137.1 466c18.1 7.6 37 12.5 56.6 15.2C240 367.1 330.5 274.4 444.2 227.7z"/>

        </g>
</svg>`;
const svgIconUrl = `data:image/svg+xml;base64,${btoa(svgIcon)}`;

export default class NetworkGraph extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            nodes: [],
            deviceModalOpen: false,
            cy: null,
            selectedNodes: [],
            connectedNodes: []
        }
        this.addNode = this.addNode.bind(this);
        this.removeNode = this.removeNode.bind(this);
        this.openDeviceModal = this.openDeviceModal.bind(this);
        this.closeDeviceModal = this.closeDeviceModal.bind(this);
        this.removeSelectedNodes = this.removeSelectedNodes.bind(this);
        this.connectNodes = this.connectNodes.bind(this);
        this.saveConfiguration = this.saveConfiguration.bind(this);
        this.getLastNetworkConf = this.getLastNetworkConf.bind(this);
        this.deselectAllNodes = this.deselectAllNodes.bind(this);
        this.listConnectedNodes = this.listConnectedNodes.bind(this);
    }

    componentDidMount() {
        this.setState({ cy: this.cy });
        this.getLastNetworkConf();
        this.cy.on('tap', 'node', this.handleNodeClick);
        this.cy.on('dragfree', 'node', this.handleNodeDragEnd);
    }

    getLastNetworkConf(){
        let h_id = getCookie('hid') ? getCookie('hid') : getCookie('user')['honeypot_id']
        toast.promise(getNetworkConf(h_id), {
            pending: "Fetch the last checkpoint"
        })
            .then(res=>res.json())
            .then(data=>{
                this.setState({
                    nodes: data.conf
                })
                this.listConnectedNodes()
            })
            .catch(err=>console.error(err))
    }

    addNode = (newNode) => {
        this.setState(prevState => ({
            nodes: [...prevState.nodes, newNode]
        }));

    }

    removeNode = (nodeId) => {
        this.setState(prevState => ({
            nodes: prevState.nodes.filter(node => node.data.id !== nodeId)
        }));

    }

    openDeviceModal(){
        this.setState({
            deviceModalOpen: true
        })
    }

    closeDeviceModal(){
        this.setState({
            deviceModalOpen: false
        })

    }

    handleNodeClick = (event) => {
        const nodeId = event.target.id();
        this.setState(prevState => {
            const updatedNodes = prevState.nodes.map(node => {
                if (node.data.id === nodeId) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            selected: !node.data.selected
                        }
                    };
                }
                return node;
            });

            const selectedNodes = updatedNodes.filter(node => node.data.selected).map(node => node.data.id);

            return {
                nodes: updatedNodes,
                selectedNodes: selectedNodes
            };
        }, () => {
            this.updateNodeStyles();
        });
    }

    updateNodeStyles = () => {
        this.state.nodes.forEach(node => {
            const cyNode = this.cy.$id(node.data.id);
            if (cyNode) {
                const color = node.data.selected ? '#333333' : 'orange';
                cyNode.style('background-color', color);
            }
        });
    }

    removeSelectedNodes = () => {
        this.setState(prevState => ({
            nodes: prevState.nodes.filter(node => !node.data.selected)
        }), () => {
            this.updateNodeStyles();
        });
    }

    handleNodeDragEnd = (event) => {
        const node = event.target;
        const nodeId = node.id();
        const newPosition = node.position();

        this.setState(prevState => ({
            nodes: prevState.nodes.map(n => {
                if (n.data.id === nodeId) {
                    return {
                        ...n,
                        position: newPosition
                    };
                }
                return n;
            })
        }));
    }

    tryToConnectTo(target){
        toast.promise(testConnection(target), {
            pending: `Testing the target ${target}`,
            success: `Honeypot ${target} is linked!`,
            error: `${target} is not an handled device`
        }).then(res=>res.json())
            .catch(err=>console.error(err))
    }

    connectNodes = () => {
        if (this.state.selectedNodes.length === 2) {
            const [source, target] = this.state.selectedNodes;
            this.tryToConnectTo(target)
            if (this.areNodesConnected(source, target)) {
                toast.error("The nodes are already connected.");
                return;
            }

            this.setState(prevState => {
                const updatedNodes = prevState.nodes.map(node => {
                    if (node.data.id === source || node.data.id === target) {

                        return {
                            ...node,
                            data: {
                                ...node.data,
                                selected: false
                            }
                        };
                    }

                    return node;
                });

                return {
                    nodes: [
                        ...updatedNodes,
                        { data: { id: `${source}-${target}`, source, target, label: `Edge from ${source} to ${target}` } }
                    ],
                    selectedNodes: []
                };
            }, () => {
                this.updateNodeStyles();
            });
        } else {
            toast.error("Please select exactly two nodes to connect.");
        }

    }

    removeEdge = () => {
        if (this.state.selectedNodes.length === 2) {
            const [source, target] = this.state.selectedNodes;

            this.setState(prevState => ({
                nodes: prevState.nodes.filter(node => !(node.data.source === source && node.data.target === target) &&
                    !(node.data.source === target && node.data.target === source)),
                selectedNodes: []
            }), () => {
                this.updateNodeStyles();
            });
        } else {
            console.log("Please select exactly two nodes to remove the connection.");
        }

    }


    areNodesConnected = (source, target) => {
        return this.state.nodes.some(node => {
            return (node.data.source === source && node.data.target === target) ||
                (node.data.source === target && node.data.target === source);
        });
    }


    saveConfiguration(){
        let data = {
            'honeypot_id': getCookie('hid') ? getCookie('hid') : getCookie('user')['honeypot_id'],
            'conf': this.state.nodes
        }
        this.deselectAllNodes()
        toast.promise(saveNetworkConf(data), {
            pending: "Saving the configuration",
            error: "Unable to save your map"
        }, {toastId: 'saveProgressionNetMapToast'})
            .then(res=>res.json())
            .then(data=>console.log(data))
            .catch(err=>console.error(err))
        this.listConnectedNodes()
    }

    listConnectedNodes = () => {
        if(this.state.nodes){
            const adminNode = this.state.nodes.find(node => node.data.label === getCookie('user').name);
            console.log(this.state.nodes)
            if (!adminNode) {
                console.log(`No node with label ${getCookie('user').name} found.`);
                return;
            }

            const adminNodeId = adminNode.data.id;

            const connectedNodes = this.state.nodes.filter(node => {
                return (node.data.source === adminNodeId || node.data.target === adminNodeId);
            });

            const connectedNodeIds = connectedNodes.map(edge => {
                return edge.data.source === adminNodeId ? edge.data.target : edge.data.source;
            });

            this.setState({ connectedNodes: connectedNodes }, () => {
                console.log('Nodes connected to admin:', this.state.connectedNodes);
            });
        }


    }

    deselectAllNodes = () => {
        this.setState(prevState => ({
            nodes: prevState.nodes.map(node => {
                if (node.data.selected) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            selected: false
                        }
                    };
                }
                return node;
            }),
            selectedNodes: []
        }), () => {
            this.updateNodeStyles();
        });
    }

    resetGraph = () => {
        this.setState({
            nodes: [
                { data: { id: 'root', label: getCookie('user').name, selected: false }, position: { x: 300, y: 0 } }
            ],
            selectedNodes: [],
            connectedNodes: []
        }, () => {
            this.updateNodeStyles();
        });
        this.saveConfiguration()
    }


    render() {
        const layout = {
            name: "circle",
            fit: true,
            animate: true
        };

        const style = {width: '100%', height: '380px', marginRight: "100px", position: "relative", marginTop: "80px"};

        const cyStyle = [
            {
                selector: 'node',
                style: {
                    'background-color': 'darkorange',
                    'background-image': svgIconUrl,
                    'label': 'data(label)',
                    'background-fit': 'contain',
                    'width': 50,
                    'height': 50,
                    'text-valign': 'top',
                    'text-halign': 'center', // Centre le texte horizontalement
                    'text-margin-y': '-5px',
                    'color': 'rgba(251,123,33,0.58)',
                    'font-size': '13px',
                    'font-family': 'Space Grotesk, sans-serif',
                    'font-weight': 700,
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ];

        return (
            <>
                <DeviceModal isOpen={this.state.deviceModalOpen} addDevice={this.addNode} closeModal={this.closeDeviceModal}/>
                <div className="info" style={{position: "fixed"}}>
                    <i className="fa-regular fa-circle-question"></i>
                    <span>The network playground let you see all devices connected to your honeypot, your gateway (default),
                        and real-times connection by hackers. Features can be display by clicking on a node (device).
                        </span>
                </div>
                <div className="network-graph">
                    <div>
                        <div className="device-card">
                            <span className="title">Devices connected</span>
                            <small>
                                <i className="fa-solid fa-circle-info"></i>
                                View devices linked in the network graph, and see their status
                            </small>
                            <div className="devices-list">
                                {this.state.connectedNodes && this.state.connectedNodes.map(connectNode => (
                                    <div className="device">
                                        <div className="device-name">
                                            <i className="fa-solid fa-desktop"></i>
                                            <span>{connectNode.data.target}</span>
                                        </div>
                                        <i className="fa-solid fa-circle fa-xs fa-fade"></i>
                                    </div>
                                ))}

                            </div>
                        </div>
                        <div className="controls">
                            {this.state.selectedNodes.length > 0 && (
                                <div>
                                    {this.state.selectedNodes.length === 2 && (
                                        <>
                                            <button onClick={this.connectNodes}>
                                                <i className="fa-solid fa-link"></i>
                                                Connect
                                            </button>
                                            <button onClick={this.removeEdge}>
                                                <i className="fa-solid fa-trash"></i>
                                                Remove
                                            </button>
                                        </>
                                    )}
                                </div>
                            )}
                            <button onClick={this.openDeviceModal}>
                                <i className="fa-solid fa-add"></i>
                                Device
                            </button>
                            <button onClick={this.saveConfiguration}>
                                <i className="fa-solid fa-save"></i>
                                Save
                            </button>
                            <button onClick={this.resetGraph}>
                                <i className="fa-solid fa-broom"></i>
                                Reset my graph
                            </button>
                        </div>
                    </div>
                    {this.state.nodes && (
                        <CytoscapeComponent
                            cy={(cy) => {
                                this.cy = cy;
                            }}
                            elements={this.state.nodes}
                            style={style}
                            layout={layout}
                            stylesheet={cyStyle}
                        />
                    )}


                </div>
            </>
        )
    }
}