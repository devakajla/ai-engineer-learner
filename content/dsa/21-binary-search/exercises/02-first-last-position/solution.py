def search_range(nums, target):
    def find(go_left):
        lo, hi = 0, len(nums) - 1
        answer = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                answer = mid
                if go_left:
                    hi = mid - 1
                else:
                    lo = mid + 1
            elif nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return answer

    return [find(True), find(False)]
