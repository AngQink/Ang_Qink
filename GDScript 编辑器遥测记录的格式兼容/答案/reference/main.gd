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
        var w: int = 0
        if (a == 1):
            p = (-1)
            u = ((((((c * 23) + s0[b]) + (e * 11)) + (b * 33)) + 37) % 251)
            if (u == d):
                w = (((((s0[b] * 33) + (e * 51)) + b) + 37) % 2048)
                v = ((((c + 2048) - w) * 1775) % 2048)
                if (v < 1024):
                    s = (v % 4)
                    v = floori(float(v) / float(4))
                    q = (v % 8)
                    v = floori(float(v) / float(8))
                    r = (v % 32)
                    v = floori(float(v) / float(32))
                    r = (r - 16)
                    s0[b] = (((c + d) + s0[b]) % 2048)
                    p = 1
        result.store_line("%d %d %d %d" % [p,q,r,s])
    result.close()
    input.close()
    quit()
