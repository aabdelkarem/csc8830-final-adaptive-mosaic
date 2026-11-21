import Foundation
import AVFoundation
import CoreGraphics
import ImageIO

let root = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let output = root.appendingPathComponent("Mosaic_30_Seconds_SILENT_DRAFT.mp4")
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
 AVVideoCodecKey: AVVideoCodecType.h264,
 AVVideoWidthKey: 1280, AVVideoHeightKey: 720,
 AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 2500000]
])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input,
 sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,
 kCVPixelBufferWidthKey as String:1280,kCVPixelBufferHeightKey as String:720,
 kCVPixelBufferCGImageCompatibilityKey as String:true,
 kCVPixelBufferCGBitmapContextCompatibilityKey as String:true])
writer.add(input)
guard writer.startWriting() else { throw writer.error! }
writer.startSession(atSourceTime: .zero)
var buffers:[CVPixelBuffer]=[]
for n in 0..<6 {
 let source = CGImageSourceCreateWithURL(root.appendingPathComponent("video_frames/\(n).png") as CFURL,nil)!
 let image = CGImageSourceCreateImageAtIndex(source,0,nil)!
 var pb:CVPixelBuffer?
 let status=CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&pb)
 guard status==kCVReturnSuccess,let pixel=pb else { fatalError("Pixel buffer allocation failed") }
 CVPixelBufferLockBaseAddress(pixel,[])
 let context=CGContext(data:CVPixelBufferGetBaseAddress(pixel),width:1280,height:720,
 bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(pixel),space:CGColorSpaceCreateDeviceRGB(),
 bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
 context.draw(image,in:CGRect(x:0,y:0,width:1280,height:720))
 CVPixelBufferUnlockBaseAddress(pixel,[]);buffers.append(pixel)
}
for frame in 0..<300 {
 while !input.isReadyForMoreMediaData {
  if writer.status == .failed { throw writer.error! }; Thread.sleep(forTimeInterval:0.002)
 }
 let sec=Double(frame)/10.0
 let index=sec<6 ? 0 : sec<10 ? 1 : sec<14 ? 2 : sec<18 ? 3 : sec<26 ? 4 : 5
 guard adaptor.append(buffers[index],withPresentationTime:CMTime(value:Int64(frame),timescale:10)) else {throw writer.error!}
}
input.markAsFinished();writer.endSession(atSourceTime:CMTime(value:30,timescale:1))
let done=DispatchSemaphore(value:0);writer.finishWriting{done.signal()};done.wait()
guard writer.status == .completed else {throw writer.error!}
print(output.path)
