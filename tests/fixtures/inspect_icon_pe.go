// Independent linked-PE oracle. Uses debug/pe, not the COFF generator.
package main

import (
 "bytes"
 "debug/pe"
 "encoding/binary"
 "fmt"
 "os"
)
var le = binary.LittleEndian
func need(ok bool, message string) { if !ok { panic(message) } }
func main() {
 f,err:=pe.Open(os.Args[1]);if err!=nil {panic(err)};defer f.Close()
 want:=uint16(0x8664);if os.Args[3]=="arm64" {want=0xaa64};need(f.Machine==want,"PE architecture")
 section:=f.Section(".rsrc");need(section!=nil,"resource section absent")
 data,err:=section.Data();if err!=nil {panic(err)}
 resources:=map[string][]byte{}
 var walk func(uint32,[]uint32)
 walk=func(off uint32,ids []uint32){
  need(int(off)+16<=len(data),"directory bounds")
  names:=le.Uint16(data[off+12:]);need(names==0,"unexpected named resource")
  n:=le.Uint16(data[off+14:]);need(int(off)+16+int(n)*8<=len(data),"entry bounds")
  for i:=0;i<int(n);i++ {at:=off+16+uint32(i)*8;id:=le.Uint32(data[at:]);target:=le.Uint32(data[at+4:]);next:=append(append([]uint32{},ids...),id)
   if target&0x80000000!=0 {need(len(next)<3,"directory depth");walk(target&0x7fffffff,next);continue}
   need(len(next)==3 && next[2]==0,"resource language/depth")
   need(int(target)+16<=len(data),"data entry bounds");rva:=le.Uint32(data[target:]);size:=le.Uint32(data[target+4:]);need(rva>=section.VirtualAddress,"unrelocated data RVA")
   pos:=rva-section.VirtualAddress;need(uint64(pos)+uint64(size)<=uint64(len(data)),"payload bounds")
   key:=fmt.Sprint(next[0],"/",next[1]);_,exists:=resources[key];need(!exists,"duplicate resource");resources[key]=data[pos:pos+size]
  }
 }
 walk(0,nil)
 ico,err:=os.ReadFile(os.Args[2]);if err!=nil {panic(err)};need(len(ico)>=6,"ICO header")
 n:=int(le.Uint16(ico[4:]));need(n==8 && len(resources)==n+1,"resource count")
 group:=resources["14/101"];need(len(group)==6+14*n && bytes.Equal(group[:6],ico[:6]),"group header")
 for i:=0;i<n;i++ {entry:=ico[6+i*16:22+i*16];size:=le.Uint32(entry[8:]);off:=le.Uint32(entry[12:]);need(uint64(off)+uint64(size)<=uint64(len(ico)),"ICO bounds")
  g:=group[6+i*14:20+i*14];need(bytes.Equal(g[:12],entry[:12]) && le.Uint16(g[12:])==uint16(i+1),"group entry")
  need(bytes.Equal(resources[fmt.Sprint("3/",i+1)],ico[off:off+size]),"icon payload mismatch")
 }
 fmt.Printf("%s: %d icons, group101, relocated RVAs and exact payloads verified\n",os.Args[3],n)
}
