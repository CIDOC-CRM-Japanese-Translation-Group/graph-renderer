export type Node = { id:string; kind?:string; top:string; bottom?:string; x?:number; y?:number; };
export type Edge = { id:string; from:string; to:string; label?:string; };
export type Graph = { nodes:Node[]; edges:Edge[]; };
