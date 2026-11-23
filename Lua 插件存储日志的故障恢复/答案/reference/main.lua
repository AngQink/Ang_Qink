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
    local p, q, r, s, u = 0, 0, 0, 0, 0
    if (a ~= 0) then
        if (a == 1) then
            if (c > s0[b]) then
                if (c > s1[b]) then
                    s1[b] = c
                    s3[b] = d
                    p = 1
                end
            end
        end
        if (a == 2) then
            if (c == s1[b]) then
                if (c > s0[b]) then
                    u = (((((c * 22) + ((s3[b] + 100) * 10)) + b) + 36) % 257)
                    if (d == u) then
                        s0[b] = c
                        s1[b] = 0
                        s2[b] = s3[b]
                        s3[b] = 0
                        p = 1
                    end
                end
            end
        end
        if (a == 3) then
            s1[b] = 0
            s3[b] = 0
            p = 2
        end
        if (a == 4) then
            p = 3
        end
        q = s0[b]
        r = s2[b]
        s = s1[b]
    end
    print(table.concat({p,q,r,s}," "))
end
