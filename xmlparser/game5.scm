; scsh script for CS U670 assignment 5.
;
; Usage:
; scsh -l game5.scm

; Change this to name your game-playing program.

(define my-process '("exec/main"))

; Example:
;
; (define my-process
;   '("/proj/will/LarcenyDev/larceny" -r6rs -program myprogram))

; Don't change this.

(define larceny '/proj/will/LarcenyDev/larceny)

(define game5 'game5.sls)

(define process1
  `(,larceny -r6rs -program ,game5))

; scsh code to pipe process1 into process2 and vice versa

(define (do-cycle process1 process2)
  (call-with-values
   (lambda () (pipe))
   (lambda (r1 w1)
     (call-with-values
      (lambda () (pipe))
      (lambda (r2 w2)
        (& ,process2 (= 0 ,r1) (= 1 ,w2))
        (& ,process1 (= 0 ,r2) (= 1 ,w1)))))))

(do-cycle process1 my-process)

(exit 0)
