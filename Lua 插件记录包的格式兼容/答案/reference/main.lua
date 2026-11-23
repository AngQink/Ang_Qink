local s0={}
local s1={}
local s2={}
local s3={}
for i=0,31 do s0[i]=0; s1[i]=0; s2[i]=0; s3[i]=0 end
for line in io.lines() do
    local row = {}
    for token in line:gmatch("%S+") do row[#row+1]=tonumber(token) end
    local a,b,c,d,e,f = unpack(row)
    if a==0 then for i=0,31 do s0[i]=0; s1[i]=0; s2[i]=0; s3[i]=0 end end
    local p, q, r, s, u, v, w = 0, 0, 0, 0, 0, 0, 0
    if (a == 1) then
        p = (-1)
        u = ((((((c * 22) + s0[b]) + (e * 10)) + (b * 32)) + 36) % 251)
        if (u == d) then
            w = (((((s0[b] * 32) + (e * 49)) + b) + 36) % 2048)
            v = ((((c + 2048) - w) * 1733) % 2048)
            if (v < 1024) then
                r = (v % 32)
                v = math.floor(v / 32)
                s = (v % 4)
                v = math.floor(v / 4)
                q = (v % 8)
                v = math.floor(v / 8)
                r = (r - 16)
                s0[b] = (((c + d) + s0[b]) % 2048)
                p = 1
            end
        end
    end
    print(table.concat({p,q,r,s}," "))
end
