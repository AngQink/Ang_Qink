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
    local p, q, r, s, u, v = 0, 0, 0, 0, 0, 0
    if (a ~= 0) then
        if (a == 2) then
            if (c > s0[b]) then
                s0[b] = c
                s1[b] = d
                s2[b] = 0
                s3[b] = 0
                p = 1
            end
        end
        if (a == 3) then
            p = 2
        end
        if (a == 1) then
            if (c <= s0[b]) then
                u = (d - s1[b])
                if (u > 0) then
                    v = (s2[b] + e)
                    if (v >= 0) then
                        if (v <= 120) then
                            s1[b] = d
                            s2[b] = v
                            s3[b] = f
                            p = 1
                        end
                    end
                end
            end
        end
        q = s0[b]
        r = s1[b]
        s = s2[b]
    end
    print(table.concat({p,q,r,s}," "))
end
