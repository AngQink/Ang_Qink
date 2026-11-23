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
            u = math.floor(c / 6)
            if ((c % 6) ~= 0) then
                u = (u + 1)
            end
            s0[b] = 1
            s1[b] = (u + (e * 21))
            if (d == 0) then
                s0[b] = 0
                s1[b] = 0
            end
        end
        if (a == 2) then
            s2[b] = c
            s3[b] = 0
            if (c == 1) then
                s3[b] = d
            end
        end
        if (s2[b] == 1) then
            p = 1
            q = s3[b]
        end
        if (s2[b] == 0) then
            if (s0[b] ~= 0) then
                p = 1
                q = s1[b]
            end
        end
        if (s2[b] == 2) then
            p = 2
        end
        r = s1[b]
        s = s0[b]
    end
    print(table.concat({p,q,r,s}," "))
end
