export type CollisionData={rooms:Record<string,number[][]>;solids:{name:string;min:number[];max:number[]}[]};
export function inPolygon(x:number,z:number,polygon:readonly (readonly number[])[]){let inside=false;for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){const a=polygon[i],b=polygon[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;}
export function canWalkAt(data:CollisionData,x:number,z:number,radius=.13){
 const interior=Object.values(data.rooms).some(p=>inPolygon(x,z,p));
 return interior&&!data.solids.some(b=>x>b.min[0]-radius&&x<b.max[0]+radius&&z>b.min[1]-radius&&z<b.max[1]+radius);
}
