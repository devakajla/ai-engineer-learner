import type { Video } from "@/lib/api";

/** YouTube embed that plays only the given segment, plus a plain link as fallback. */
export default function VideoSegment({ video, label }: { video: Video; label: string }) {
  const params = new URLSearchParams({ start: String(video.start), rel: "0" });
  if (video.end) params.set("end", String(video.end));
  const src = `https://www.youtube-nocookie.com/embed/${video.video_id}?${params}`;
  const href = `https://www.youtube.com/watch?v=${video.video_id}&t=${video.start}s`;
  return (
    <div className="card video-card">
      <div className="card-label">{label}</div>
      <div className="video-frame">
        <iframe src={src} title={video.title || label} allow="encrypted-media; picture-in-picture" allowFullScreen />
      </div>
      <a className="muted" href={href} target="_blank" rel="noreferrer">
        {video.title || "Open on YouTube"} ↗
      </a>
    </div>
  );
}
