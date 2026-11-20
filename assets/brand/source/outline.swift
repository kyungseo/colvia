import Foundation
import CoreGraphics
import CoreText

func number(_ x: CGFloat) -> String {
    let s = String(format:"%.6f",Double(x))
    return s.replacingOccurrences(of:"\\.?0+$",with:"",options:.regularExpression)
}
func svg(_ path: CGPath) -> String {
    var parts:[String]=[]
    path.applyWithBlock { ptr in
        let e=ptr.pointee
        func p(_ i:Int)->String { number(e.points[i].x)+" "+number(e.points[i].y) }
        switch e.type {
        case .moveToPoint: parts.append("M"+p(0))
        case .addLineToPoint: parts.append("L"+p(0))
        case .addQuadCurveToPoint: parts.append("Q"+p(0)+" "+p(1))
        case .addCurveToPoint: parts.append("C"+p(0)+" "+p(1)+" "+p(2))
        case .closeSubpath: parts.append("Z")
        @unknown default: fatalError("unsupported path")
        }
    }
    return parts.joined(separator:" ")
}
func bounds(_ p:CGPath)->[CGFloat] { let r=p.boundingBoxOfPath;return [r.minX,r.minY,r.width,r.height] }
guard CommandLine.arguments.count == 2 else {
    FileHandle.standardError.write(Data("Usage: swift outline.swift path/to/r6-1-open-c.svg\n".utf8))
    exit(64)
}
let input=URL(fileURLWithPath:CommandLine.arguments[1])
let source=try String(contentsOf:input,encoding:.utf8)
let expected="M27.9 45.7 A14 14 0 1 1 22 19 C29 19 31 30 36.5 30 C42 30 44 21 49.5 21 L56 21"
guard source.contains(expected) else { fatalError("Source geometry changed: update the explicit conversion.") }
let p=CGMutablePath()
let x1=27.9, y1=45.7, x2=22.0, y2=19.0, radius=14.0
let dx=(x1-x2)/2, dy=(y1-y2)/2
let coef = -sqrt(max(0,(radius*radius-dx*dx-dy*dy)/(dx*dx+dy*dy)))
let cx=(x1+x2)/2+coef*dy, cy=(y1+y2)/2-coef*dx
let start=atan2(y1-cy,x1-cx)
var delta=atan2(y2-cy,x2-cx)-start
if delta<0 {delta += 2 * Double.pi}
p.move(to:CGPoint(x:x1,y:y1))
let segments=Int(ceil(abs(delta)/(Double.pi/4)))
for i in 0..<segments {
    let a=start+delta*Double(i)/Double(segments), b=start+delta*Double(i+1)/Double(segments)
    let k=4.0/3.0*tan((b-a)/4)
    p.addCurve(to:CGPoint(x:cx+radius*cos(b),y:cy+radius*sin(b)),
      control1:CGPoint(x:cx+radius*(cos(a)-k*sin(a)),y:cy+radius*(sin(a)+k*cos(a))),
      control2:CGPoint(x:cx+radius*(cos(b)+k*sin(b)),y:cy+radius*(sin(b)-k*cos(b))))
}
p.addCurve(to:CGPoint(x:36.5,y:30),control1:CGPoint(x:29,y:19),control2:CGPoint(x:31,y:30))
p.addCurve(to:CGPoint(x:49.5,y:21),control1:CGPoint(x:42,y:30),control2:CGPoint(x:44,y:21))
p.addLine(to:CGPoint(x:56,y:21))
var up=CGAffineTransform(scaleX:100, y:100)
let enlarged=p.copy(using:&up)!
let expanded=enlarged.copy(strokingWithWidth:900,lineCap:.round,lineJoin:.round,miterLimit:1000)
var down=CGAffineTransform(scaleX:0.01,y:0.01)
let outlined=expanded.copy(using:&down)!
func textPath(_ text:String,_ name:String)->[String:Any] {
    let font=CTFontCreateWithName(name as CFString,64,nil)
    let actual=CTFontCopyPostScriptName(font) as String
    guard actual==name else { fatalError("Font substitution: "+actual) }
    let attr=NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font])
    let line=CTLineCreateWithAttributedString(attr)
    let path=CGMutablePath()
    let runs=CTLineGetGlyphRuns(line) as! [CTRun]
    for run in runs {
        let n=CTRunGetGlyphCount(run)
        var glyphs=[CGGlyph](repeating:0,count:n)
        var pos=[CGPoint](repeating:.zero,count:n)
        CTRunGetGlyphs(run,CFRange(location:0,length:0),&glyphs)
        CTRunGetPositions(run,CFRange(location:0,length:0),&pos)
        for i in 0..<n {
            guard let g=CTFontCreatePathForGlyph(font,glyphs[i],nil) else {continue}
            path.addPath(g,transform:CGAffineTransform(a:1,b:0,c:0,d:-1,tx:pos[i].x,ty:-pos[i].y))
        }
    }
    return ["text":text,"font":actual,"font_size":64,"advance":CTLineGetTypographicBounds(line,nil,nil,nil),"path":svg(path),"bounds":bounds(path)]
}
for name in ["Inter-SemiBold", "Inter-Medium"] {
    let url=input.deletingLastPathComponent().appendingPathComponent(name+".otf")
    var error: Unmanaged<CFError>?
    guard CTFontManagerRegisterFontsForURL(url as CFURL, .process, &error) else { fatalError("Cannot register bundled font") }
}
let result:[String:Any]=[
 "symbol":["path":svg(outlined),"bounds":bounds(outlined),"centerline_cubic":svg(p),"conversion":"CoreGraphics stroked outline; SVG circular arc approximated by cubic segments <= 45 degrees; stroke expanded at 100x then scaled back"],
 "colvia":textPath("Colvia","Inter-SemiBold"),
 "descriptor":textPath("AI Work Harness","Inter-Medium"),
 "readmeTagline":textPath("Human-led AI work","Inter-Medium")
]
let out=try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(out)
