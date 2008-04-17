; Copyright 2008 William D Clinger
;
; Tokens for the CS U670 referee
; (input only, which is the output of a game-playing program).
;
; This file is case-sensitive.
; It defines scheme_terminals, which is an input to LexGen.
; See makeLexer.sch for an example of its use.

#!no-fold-case

; The scanner generator gives priority to explicit characters,
; so these predicates can include characters that have special
; meaning when they appear within the same regular expression.

(define character-classes
  '((isAsciiNotDoublequote
     (lambda (c)
       (and (char? c)
            (char<=? c (integer->char 127))
            (not (char=? c #\")))))
    (isWordConstituent
     (lambda (c)
       (and (char? c)
            (char<=? c (integer->char 127))
            (not (char=? c #\<))
            (not (char=? c #\>))
            (not (char=? c #\=))
            (not (char=? c #\/))
            (not (char=? c #\tab))
            (not (char=? c #\linefeed))
            (not (char=? c #\vtab))
            (not (char=? c #\page))
            (not (char=? c #\return))
            (not (char=? c #\space)))))))

; Expands symbols like %a..z into (! #\a #\b ... #\z).
; FIXME: This notation assumes case-sensitive symbols.

(define (expand-ranges spec)
  (cond ((pair? spec)
         (cons (expand-ranges (car spec))
               (expand-ranges (cdr spec))))
        ((and (symbol? spec)
              (let ((s (symbol->string spec)))
                (and (= 5 (string-length s))
                     (char=? (string-ref s 0) #\%)
                     (char=? (string-ref s 2) #\.)
                     (char=? (string-ref s 3) #\.)
                     s)))
         =>
         (lambda (s)
           (let* ((c1 (string-ref s 1))
                  (c2 (string-ref s 4))
                  (n2 (char->integer c2)))
             (do ((i (char->integer c1) (+ i 1))
                  (chars '() (cons (integer->char i) chars)))
                 ((> i n2)
                  (cons '! (reverse chars)))))))
        (else spec)))

; Regular expressions for the referee's input tokens.

(define scheme_terminals
  (expand-ranges
   '(

     ; The scanner generator treats whitespace specially.

     (whitespace (! #\tab #\linefeed #\vtab #\page #\return #\space))

     (lt (#\<))

     (gt (#\>))

     (slash (#\/))

     (eq (#\=))

     (doublequote (#\"))

     (word (isWordConstituent (* isWordConstituent)))

     (string (#\" (* isAsciiNotDoublequote) #\"))

     (int ((! () #\+ #\-)
           (%0..9 (* %0..9)))))))
