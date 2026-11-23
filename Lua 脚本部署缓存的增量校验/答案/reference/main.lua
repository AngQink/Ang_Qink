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
    local p, q, r, s = 0, 0, 0, 0
    if (a ~= 0) then
        if (a == 1) then
            s0[b] = (((((((c * 49) + (d * 32)) + (e * 7)) + f) + 36) % 4093) + 1)
            s1[b] = (((((d * 22) + (f * 10)) + (e * 23)) % 1297) + 1)
        end
        if (a == 2) then
            if (s0[b] ~= 0) then
                if (c == s0[b]) then
                    if (d == s1[b]) then
                        s2[b] = c
                        s3[b] = d
                        p = 1
                    end
                end
            end
        end
        if (a == 3) then
            if (s2[b] ~= 0) then
                if (c == s2[b]) then
                    if (d == s3[b]) then
                        s2[b] = 0
                        s3[b] = 0
                        p = 1
                    end
                end
            end
        end
        q = s0[b]
        r = s1[b]
        if (q ~= 0) then
            if (q == s2[b]) then
                if (r == s3[b]) then
                    s = 1
                end
            end
            if (a == 1) then
                p = (3 - s)
            end
            if (a == 4) then
                p = (3 - s)
            end
        end
    end
    print(table.concat({p,q,r,s}," "))
end
