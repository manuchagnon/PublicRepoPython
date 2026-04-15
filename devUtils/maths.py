def remap_value(x, old_start, old_end, new_start, new_end):
    return new_start + ((x - old_start) / (old_end - old_start)) * (new_end - new_start)