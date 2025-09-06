function important(w=40, h=20)
    for j in 1:h
        y = 1.2 - 2.4*(j-1)/(h-1) 
        line = ""
        for i in 1:w
            x = -1.5 + 3.0*(i-1)/(w-1) 
            val = (x^2 + y^2 - 1)^3 - x^2 * y^3
            line *= val <= 0 ? "██" : "  "
        end
        println(line)
    end
end

important(36,18)
