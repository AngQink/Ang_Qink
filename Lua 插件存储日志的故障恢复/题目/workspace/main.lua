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
        p = 0
    end
    print(table.concat({p,q,r,s}," "))
end
