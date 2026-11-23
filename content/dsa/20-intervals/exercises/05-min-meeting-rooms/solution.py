def min_meeting_rooms(meetings):
    starts = sorted(m[0] for m in meetings)
    ends = sorted(m[1] for m in meetings)
    rooms = 0
    j = 0
    for s in starts:
        if s >= ends[j]:
            j += 1
        else:
            rooms += 1
    return rooms
