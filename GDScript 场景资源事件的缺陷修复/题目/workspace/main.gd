extends SceneTree

func _initialize() -> void:
    var input := FileAccess.open("res://input.txt",FileAccess.READ)
    var result := FileAccess.open("res://result.txt",FileAccess.WRITE)
    var s0: Array[int] = []
    s0.resize(32)
    s0.fill(0)
    var s1: Array[int] = []
    s1.resize(32)
    s1.fill(0)
    var s2: Array[int] = []
    s2.resize(32)
    s2.fill(0)
    var s3: Array[int] = []
    s3.resize(32)
    s3.fill(0)
    while input.get_position()<input.get_length():
        var row := input.get_line().split(" ",false)
        var a: int = row[0].to_int()
        var b: int = row[1].to_int()
        var c: int = row[2].to_int()
        var d: int = row[3].to_int()
        var e: int = row[4].to_int()
        var f: int = row[5].to_int()
        if a==0:
            s0.fill(0)
            s1.fill(0)
            s2.fill(0)
            s3.fill(0)
        var p: int = 0
        var q: int = 0
        var r: int = 0
        var s: int = 0
        var u: int = 0
        var v: int = 0
        if (a != 0):
            if (a == 2):
                if (c > s0[b]):
                    s0[b] = c
                    s1[b] = d
                    s2[b] = 0
                    s3[b] = 0
                    p = 1
            if (a == 3):
                p = 2
            if (a == 1):
                if (c <= s0[b]):
                    u = (((d + 64) - s1[b]) % 64)
                    if (u > 0):
                        if (u < 32):
                            v = (s2[b] + e)
                            if (v >= 0):
                                if (v <= 123):
                                    s1[b] = d
                                    s2[b] = v
                                    s3[b] = f
                                    p = 1
            q = s0[b]
            r = s1[b]
            s = s2[b]
        result.store_line("%d %d %d %d" % [p,q,r,s])
    result.close()
    input.close()
    quit()
