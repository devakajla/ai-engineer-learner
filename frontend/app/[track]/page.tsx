"use client";

// Opening a track jumps to the next lesson you haven't finished.
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function TrackPage() {
  const { track } = useParams<{ track: string }>();
  const router = useRouter();
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .track(track)
      .then((t) => {
        if (t.next_up) router.replace(`/${track}/${t.next_up.slug}`);
        else setError("This track has no lessons yet.");
      })
      .catch((e) => setError(e.message));
  }, [track, router]);

  return <div className="center-msg">{error || "Loading…"}</div>;
}
