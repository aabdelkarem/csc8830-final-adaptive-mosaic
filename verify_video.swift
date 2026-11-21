import Foundation
import AVFoundation
import ImageIO
import UniformTypeIdentifiers
let url=URL(fileURLWithPath:CommandLine.arguments[1])
let asset=AVURLAsset(url:url)
let duration=CMTimeGetSeconds(asset.duration)
let audio=asset.tracks(withMediaType:.audio).count
guard abs(duration-30.0)<0.0001,audio==0 else {fatalError("Unexpected duration or audio")}
let generator=AVAssetImageGenerator(asset:asset)
generator.appliesPreferredTrackTransform=true
let image=try generator.copyCGImage(at:.zero,actualTime:nil)
let dest=CGImageDestinationCreateWithURL(URL(fileURLWithPath:"/tmp/cv-video-first-frame.png") as CFURL,UTType.png.identifier as CFString,1,nil)!
CGImageDestinationAddImage(dest,image,nil);CGImageDestinationFinalize(dest)
print("duration_seconds=\(duration) audio_tracks=\(audio) video_tracks=\(asset.tracks(withMediaType:.video).count)")
