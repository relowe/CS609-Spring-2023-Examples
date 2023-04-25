(let
    (
        (create_count 
            (lambda (by) (lambda (x) (+ x by)))
        )        
        (x 12)
    )

    (let 
        (
            (by5 (create_count 5))
            (by10 (create_count 10))
            (x -5)
        )

        (print (by5 0))
        (print (by10 0)) 
        (print x)
    )

    (print x)
)