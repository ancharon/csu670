;;; This file contains ERR5RS/R6RS libraries followed by
;;; an ERR5RS/R6RS top-level program.


(library (local parse-xml-message)
  (export parse-xml-message)
  (import (rnrs) (rnrs mutable-strings))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Parser for the referee's input messages.
;;;
;;; Based in part on Larceny's src/Lib/Common/reader.sch
;;;
;;; Usage:
;;; (parse-xml-message input-port) reads an output message,
;;; as specified by CS U670 assignment 7, from input-port
;;; and returns a representation of it as a list generated
;;; by the following grammar.  Note: this representation
;;; is not SXML because it has no *TOP*, but has the form
;;; of an SXML element.
;;;
;;; <message>  -->  (stop)
;;;              |  (enter)
;;;              |  (exit <direction>)
;;;              |  (grasp <item>)
;;;              |  (drop)
;;;              |  (write <text>)
;;;              |  (assault)
;;;              |  (error <string>)
;;; <direction>  -->  up  |  down  |  north  |  east  |  south  |  west
;;; <item>  -->  (frog)
;;;           |  (paper <text>)
;;;           |  (treasure (@ (style <string>)) <int>)
;;;           |  (shield (@ (style <string>)) <int>)
;;;           |  (weapon (@ (style <string>)) <int>)
;;; <text>  -->  <string>
;;; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (parse-xml-message input-port)

  ; Constants and local variables.

  (let* (; Constants.

         ; initial length of string_accumulator

         (initial_accumulator_length 64)

         ; Encodings of error messages.

         (errIncompleteToken 1)      ; any lexical error, really
         (errBug 9)            ; bug in reader, shouldn't happen
         (errLexGenBug 10)                        ; can't happen

         ; FIXME: this shouldn't be necessary

         (EOF #\x04)

         ; State for one-token buffering in lexical analyzer.

         (kindOfNextToken 'z1)      ; valid iff nextTokenIsReady
         (nextTokenIsReady #f)

         (tokenValue "")  ; string associated with current token

         ; A string buffer for the characters of the current token.
         ; Resized as necessary.

         (string_accumulator (make-string initial_accumulator_length))

         ; Number of characters in string_accumulator.

         (string_accumulator_length 0)

         (reserved-words
          '(("stop" . stop)
            ("enter" . enter)
            ("exit" . exit)
            ("up" . up)
            ("down" . down)
            ("north" . north)
            ("east" . east)
            ("south" . south)
            ("west" . west)
            ("grasp" . grasp)
            ("frog" . frog)
            ("paper" . paper)
            ("treasure" . treasure)
            ("style" . style)
            ("shield" . shield)
            ("weapon" . weapon)
            ("drop" . drop)
            ("write" . write)
            ("assault" . assault)))

        )

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; LexGen generated the code for the state machine.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
(define (scanner0)
  (define (state0 c)
    (case c
      ((#\=) (consumeChar) (accept 'eq))
      ((#\/) (consumeChar) (accept 'slash))
      ((#\>) (consumeChar) (accept 'gt))
      ((#\<) (consumeChar) (accept 'lt))
      ((#\tab #\newline #\vtab #\page #\return #\space)
       (consumeChar)
       (begin
         (set! string_accumulator_length 0)
         (state0 (scanChar))))
      ((#\") (consumeChar) (state5 (scanChar)))
      ((#\+ #\-) (consumeChar) (state2 (scanChar)))
      ((#\0 #\1 #\2 #\3 #\4 #\5 #\6 #\7 #\8 #\9)
       (consumeChar)
       (state1 (scanChar)))
      (else
       (if ((lambda (c)
              (and (char? c)
                   (char<=? c (integer->char 127))
                   (not (char=? c #\<))
                   (not (char=? c #\>))
                   (not (char=? c #\=))
                   (not (char=? c #\/))
                   (not (char=? c #\tab))
                   (not (char=? c #\newline))
                   (not (char=? c #\vtab))
                   (not (char=? c #\page))
                   (not (char=? c #\return))
                   (not (char=? c #\space))))
            c)
           (begin (consumeChar) (state3 (scanChar)))
           (scannerError errIncompleteToken)))))
  (define (state1 c)
    (case c
      ((#\0 #\1 #\2 #\3 #\4 #\5 #\6 #\7 #\8 #\9)
       (consumeChar)
       (state1 (scanChar)))
      (else (accept 'int))))
  (define (state2 c)
    (case c
      ((#\0 #\1 #\2 #\3 #\4 #\5 #\6 #\7 #\8 #\9)
       (consumeChar)
       (state1 (scanChar)))
      (else (scannerError errIncompleteToken))))
  (define (state3 c)
    (case c
      (else
       (if ((lambda (c)
              (and (char? c)
                   (char<=? c (integer->char 127))
                   (not (char=? c #\<))
                   (not (char=? c #\>))
                   (not (char=? c #\=))
                   (not (char=? c #\/))
                   (not (char=? c #\tab))
                   (not (char=? c #\newline))
                   (not (char=? c #\vtab))
                   (not (char=? c #\page))
                   (not (char=? c #\return))
                   (not (char=? c #\space))))
            c)
           (begin (consumeChar) (state3 (scanChar)))
           (accept 'word)))))
  (define (state4 c)
    (case c
      ((#\") (consumeChar) (accept 'string))
      (else
       (if ((lambda (c)
              (and (char? c)
                   (char<=? c (integer->char 127))
                   (not (char=? c #\"))))
            c)
           (begin (consumeChar) (state4 (scanChar)))
           (scannerError errIncompleteToken)))))
  (define (state5 c)
    (case c
      ((#\") (consumeChar) (accept 'string))
      (else
       (if ((lambda (c)
              (and (char? c)
                   (char<=? c (integer->char 127))
                   (not (char=? c #\"))))
            c)
           (begin (consumeChar) (state4 (scanChar)))
           (accept 'doublequote)))))
  (define (state6 c)
    (case c
      (else
       (begin
         (set! string_accumulator_length 0)
         (state0 (scanChar))))))
  (define (state7 c) (case c (else (accept 'lt))))
  (define (state8 c) (case c (else (accept 'gt))))
  (define (state9 c)
    (case c (else (accept 'slash))))
  (define (state10 c) (case c (else (accept 'eq))))
  (define (state11 c)
    (case c (else (accept 'string))))
  (let loop ((c (scanChar)))
    (if (char-whitespace? c)
        (begin
          (consumeChar)
          (set! string_accumulator_length 0)
          (loop (scanChar)))))
  (let ((c (scanChar)))
    (if (char=? c EOF) (accept 'eof) (state0 c))))

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; End of state machine generated by LexGen.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; ParseGen generated the code for the strong LL(1) parser.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
(define (parse-message)
  (case (next-token)
    ((lt)
     (begin
       (consume-token!)
       (let ((ast1 (parse-message2))) (identity ast1))))
    (else (parse-error '<message> '(lt)))))

(define (parse-message2)
  (case (next-token)
    ((assault)
     (begin
       (consume-token!)
       (let ((ast1 (parse-assault2))) (identity ast1))))
    ((write)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin
             (consume-token!)
             (let ((ast1 (parse-text)))
               (if (eq? (next-token) 'lt)
                   (begin
                     (consume-token!)
                     (if (eq? (next-token) 'slash)
                         (begin
                           (consume-token!)
                           (if (eq? (next-token) 'write)
                               (begin
                                 (consume-token!)
                                 (if (eq? (next-token) 'gt)
                                     (begin (consume-token!) (makeWrite ast1))
                                     (parse-error '<message2> '(gt))))
                               (parse-error '<message2> '(write))))
                         (parse-error '<message2> '(slash))))
                   (parse-error '<message2> '(lt)))))
           (parse-error '<message2> '(gt)))))
    ((drop)
     (begin
       (consume-token!)
       (let ((ast1 (parse-drop2))) (identity ast1))))
    ((grasp)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin
             (consume-token!)
             (let ((ast1 (parse-item)))
               (if (eq? (next-token) 'lt)
                   (begin
                     (consume-token!)
                     (if (eq? (next-token) 'slash)
                         (begin
                           (consume-token!)
                           (if (eq? (next-token) 'grasp)
                               (begin
                                 (consume-token!)
                                 (if (eq? (next-token) 'gt)
                                     (begin (consume-token!) (makeGrasp ast1))
                                     (parse-error '<message2> '(gt))))
                               (parse-error '<message2> '(grasp))))
                         (parse-error '<message2> '(slash))))
                   (parse-error '<message2> '(lt)))))
           (parse-error '<message2> '(gt)))))
    ((exit)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin
             (consume-token!)
             (let ((ast1 (parse-direction)))
               (if (eq? (next-token) 'lt)
                   (begin
                     (consume-token!)
                     (if (eq? (next-token) 'slash)
                         (begin
                           (consume-token!)
                           (if (eq? (next-token) 'exit)
                               (begin
                                 (consume-token!)
                                 (if (eq? (next-token) 'gt)
                                     (begin (consume-token!) (makeExit ast1))
                                     (parse-error '<message2> '(gt))))
                               (parse-error '<message2> '(exit))))
                         (parse-error '<message2> '(slash))))
                   (parse-error '<message2> '(lt)))))
           (parse-error '<message2> '(gt)))))
    ((enter)
     (begin
       (consume-token!)
       (let ((ast1 (parse-enter2))) (identity ast1))))
    ((stop)
     (begin
       (consume-token!)
       (let ((ast1 (parse-stop2))) (identity ast1))))
    (else
     (parse-error
       '<message2>
       '(assault drop enter exit grasp stop write)))))

(define (parse-stop2)
  (case (next-token)
    ((slash)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin (consume-token!) (makeStop))
           (parse-error '<stop2> '(gt)))))
    ((gt)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'lt)
           (begin
             (consume-token!)
             (if (eq? (next-token) 'slash)
                 (begin
                   (consume-token!)
                   (if (eq? (next-token) 'stop)
                       (begin
                         (consume-token!)
                         (if (eq? (next-token) 'gt)
                             (begin (consume-token!) (makeStop))
                             (parse-error '<stop2> '(gt))))
                       (parse-error '<stop2> '(stop))))
                 (parse-error '<stop2> '(slash))))
           (parse-error '<stop2> '(lt)))))
    (else (parse-error '<stop2> '(gt slash)))))

(define (parse-enter2)
  (case (next-token)
    ((slash)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin (consume-token!) (makeEnter))
           (parse-error '<enter2> '(gt)))))
    ((gt)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'lt)
           (begin
             (consume-token!)
             (if (eq? (next-token) 'slash)
                 (begin
                   (consume-token!)
                   (if (eq? (next-token) 'enter)
                       (begin
                         (consume-token!)
                         (if (eq? (next-token) 'gt)
                             (begin (consume-token!) (makeEnter))
                             (parse-error '<enter2> '(gt))))
                       (parse-error '<enter2> '(enter))))
                 (parse-error '<enter2> '(slash))))
           (parse-error '<enter2> '(lt)))))
    (else (parse-error '<enter2> '(gt slash)))))

(define (parse-drop2)
  (case (next-token)
    ((slash)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin (consume-token!) (makeDrop))
           (parse-error '<drop2> '(gt)))))
    ((gt)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'lt)
           (begin
             (consume-token!)
             (if (eq? (next-token) 'slash)
                 (begin
                   (consume-token!)
                   (if (eq? (next-token) 'drop)
                       (begin
                         (consume-token!)
                         (if (eq? (next-token) 'gt)
                             (begin (consume-token!) (makeDrop))
                             (parse-error '<drop2> '(gt))))
                       (parse-error '<drop2> '(drop))))
                 (parse-error '<drop2> '(slash))))
           (parse-error '<drop2> '(lt)))))
    (else (parse-error '<drop2> '(gt slash)))))

(define (parse-assault2)
  (case (next-token)
    ((slash)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin (consume-token!) (makeAssault))
           (parse-error '<assault2> '(gt)))))
    ((gt)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'lt)
           (begin
             (consume-token!)
             (if (eq? (next-token) 'slash)
                 (begin
                   (consume-token!)
                   (if (eq? (next-token) 'assault)
                       (begin
                         (consume-token!)
                         (if (eq? (next-token) 'gt)
                             (begin (consume-token!) (makeAssault))
                             (parse-error '<assault2> '(gt))))
                       (parse-error '<assault2> '(assault))))
                 (parse-error '<assault2> '(slash))))
           (parse-error '<assault2> '(lt)))))
    (else (parse-error '<assault2> '(gt slash)))))

(define (parse-direction)
  (case (next-token)
    ((west) (begin (consume-token!) (makeWest)))
    ((south) (begin (consume-token!) (makeSouth)))
    ((east) (begin (consume-token!) (makeEast)))
    ((north) (begin (consume-token!) (makeNorth)))
    ((down) (begin (consume-token!) (makeDown)))
    ((up) (begin (consume-token!) (makeUp)))
    (else
     (parse-error
       '<direction>
       '(down east north south up west)))))

(define (parse-item)
  (case (next-token)
    ((lt)
     (begin
       (consume-token!)
       (let ((ast1 (parse-item2))) (identity ast1))))
    (else (parse-error '<item> '(lt)))))

(define (parse-item2)
  (case (next-token)
    ((weapon)
     (begin
       (consume-token!)
       (let ((ast1 (parse-style)))
         (if (eq? (next-token) 'gt)
             (begin
               (consume-token!)
               (let ((ast2 (parse-int)))
                 (if (eq? (next-token) 'lt)
                     (begin
                       (consume-token!)
                       (if (eq? (next-token) 'slash)
                           (begin
                             (consume-token!)
                             (if (eq? (next-token) 'weapon)
                                 (begin
                                   (consume-token!)
                                   (if (eq? (next-token) 'gt)
                                       (begin
                                         (consume-token!)
                                         (makeWeapon ast1 ast2))
                                       (parse-error '<item2> '(gt))))
                                 (parse-error '<item2> '(weapon))))
                           (parse-error '<item2> '(slash))))
                     (parse-error '<item2> '(lt)))))
             (parse-error '<item2> '(gt))))))
    ((shield)
     (begin
       (consume-token!)
       (let ((ast1 (parse-style)))
         (if (eq? (next-token) 'gt)
             (begin
               (consume-token!)
               (let ((ast2 (parse-int)))
                 (if (eq? (next-token) 'lt)
                     (begin
                       (consume-token!)
                       (if (eq? (next-token) 'slash)
                           (begin
                             (consume-token!)
                             (if (eq? (next-token) 'shield)
                                 (begin
                                   (consume-token!)
                                   (if (eq? (next-token) 'gt)
                                       (begin
                                         (consume-token!)
                                         (makeShield ast1 ast2))
                                       (parse-error '<item2> '(gt))))
                                 (parse-error '<item2> '(shield))))
                           (parse-error '<item2> '(slash))))
                     (parse-error '<item2> '(lt)))))
             (parse-error '<item2> '(gt))))))
    ((treasure)
     (begin
       (consume-token!)
       (let ((ast1 (parse-style)))
         (if (eq? (next-token) 'gt)
             (begin
               (consume-token!)
               (let ((ast2 (parse-int)))
                 (if (eq? (next-token) 'lt)
                     (begin
                       (consume-token!)
                       (if (eq? (next-token) 'slash)
                           (begin
                             (consume-token!)
                             (if (eq? (next-token) 'treasure)
                                 (begin
                                   (consume-token!)
                                   (if (eq? (next-token) 'gt)
                                       (begin
                                         (consume-token!)
                                         (makeTreasure ast1 ast2))
                                       (parse-error '<item2> '(gt))))
                                 (parse-error '<item2> '(treasure))))
                           (parse-error '<item2> '(slash))))
                     (parse-error '<item2> '(lt)))))
             (parse-error '<item2> '(gt))))))
    ((paper)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin
             (consume-token!)
             (let ((ast1 (parse-text)))
               (if (eq? (next-token) 'lt)
                   (begin
                     (consume-token!)
                     (if (eq? (next-token) 'slash)
                         (begin
                           (consume-token!)
                           (if (eq? (next-token) 'paper)
                               (begin
                                 (consume-token!)
                                 (if (eq? (next-token) 'gt)
                                     (begin (consume-token!) (makePaper ast1))
                                     (parse-error '<item2> '(gt))))
                               (parse-error '<item2> '(paper))))
                         (parse-error '<item2> '(slash))))
                   (parse-error '<item2> '(lt)))))
           (parse-error '<item2> '(gt)))))
    ((frog)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'gt)
           (begin
             (consume-token!)
             (if (eq? (next-token) 'lt)
                 (begin
                   (consume-token!)
                   (if (eq? (next-token) 'slash)
                       (begin
                         (consume-token!)
                         (if (eq? (next-token) 'frog)
                             (begin
                               (consume-token!)
                               (if (eq? (next-token) 'gt)
                                   (begin (consume-token!) (makeFrog))
                                   (parse-error '<item2> '(gt))))
                             (parse-error '<item2> '(frog))))
                       (parse-error '<item2> '(slash))))
                 (parse-error '<item2> '(lt))))
           (parse-error '<item2> '(gt)))))
    (else
     (parse-error
       '<item2>
       '(frog paper shield treasure weapon)))))

(define (parse-style)
  (case (next-token)
    ((style)
     (begin
       (consume-token!)
       (if (eq? (next-token) 'eq)
           (begin
             (consume-token!)
             (let ((ast1 (parse-string))) (makeStyle ast1)))
           (parse-error '<style> '(eq)))))
    (else (parse-error '<style> '(style)))))

(define (parse-string)
  (case (next-token)
    ((string) (begin (consume-token!) (makeString)))
    (else (parse-error '<string> '(string)))))

(define (parse-text)
  (case (next-token)
    ((word)
     (let ((ast1 (parse-word)))
       (let ((ast2 (parse-text)))
         (makeWordText ast1 ast2))))
    ((lt) (makeEmptyText))
    (else (parse-error '<text> '(lt word)))))

(define (parse-word)
  (case (next-token)
    ((word) (begin (consume-token!) (makeWord)))
    (else (parse-error '<word> '(word)))))

(define (parse-int)
  (case (next-token)
    ((int) (begin (consume-token!) (makeInt)))
    (else (parse-error '<int> '(int)))))

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; End of LL(1) parser generated by ParseGen.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; Lexical analyzer.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
    ; next-token and consume-token! are called by the parser.
  
    ; Returns the current token.
  
    (define (next-token)
      (if nextTokenIsReady
          kindOfNextToken
          (begin (set! string_accumulator_length 0)
                 (scanner0))))
  
    ; Consumes the current token.
  
    (define (consume-token!)
      (set! nextTokenIsReady #f))
  
    ; Called by the lexical analyzer's state machine.
  
    (define (scannerError msg)
      (define msgtxt
        (cond ((= msg errIncompleteToken)
               "Incomplete or illegal token")
              ((= msg errLexGenBug)
               "Bug in lexical analyzer (generated)")
              (else "Bug in lexical analyzer")))
      (let* ((c (scanChar))
             (next (if (char? c) (string c) ""))
             (msgtxt (string-append msgtxt
                                    ": "
                                    (substring string_accumulator
                                               0
                                               string_accumulator_length)
                                    next)))

        ; must avoid infinite loop on current input port

        (consumeChar)
        (error 'get-datum
               (string-append "Lexical Error: " msgtxt " ")
               input-port))
      (next-token))
  
    ; Accepts a token of the given kind, returning that kind.
    ;
    ; For some kinds of tokens, a value for the token must also
    ; be recorded in tokenValue.  Most of those tokens must be
    ; followed by a delimiter.
    ;
    ; Some magical tokens require special processing.
  
    (define (accept t)
      (case t
       ((word string int)
        (set! tokenValue
              (substring string_accumulator
                         0 string_accumulator_length))
        (if (eq? t 'string)
            (set! tokenValue
                  (substring tokenValue
                             1
                             (- (string-length tokenValue) 1))))))

      (set! kindOfNextToken t)
      (set! nextTokenIsReady #t)
      (let ((t (if (eq? t 'word)
                   (or (reserved-word? tokenValue) t)
                   t)))
        t))

    (define (reserved-word? s)
      (let ((probe (assoc s reserved-words)))
        (if probe
            (cdr probe)
            #f)))

    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; Character i/o, so to speak.
    ; Uses the input-port as input.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
    (define (scanChar)
      (peek-char input-port))

    ; Consumes the current character.  Returns unspecified values.
  
    (define (consumeChar)
      (if (< string_accumulator_length (string-length string_accumulator))
          (let ((c (read-char input-port)))
            (if (char? c)
                (begin
                 (string-set! string_accumulator
                              string_accumulator_length
                              c)
                 (set! string_accumulator_length
                       (+ string_accumulator_length 1)))))
          (begin (expand-accumulator) (consumeChar))))

    ; Doubles the size of string_accumulator while
    ; preserving its contents.

    (define (expand-accumulator)
      (let* ((n (string-length string_accumulator))
             (new (make-string (* 2 n))))
        (do ((i 0 (+ i 1)))
            ((= i n))
          (string-set! new i (string-ref string_accumulator i)))
        (set! string_accumulator new)))
  
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; Action procedures called by the parser.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    (define (identity x) x)

    (define (makeAssault) '(assault))

    (define (makeDown) 'down)

    (define (makeDrop) '(drop))

    (define (makeEast) 'east)

    (define (makeEmptyText) "")

    (define (makeEnter) '(enter))

    (define (makeExit <direction>) (list 'exit <direction>))

    (define (makeFrog) '(frog))

    (define (makeGrasp <item>) (list 'grasp <item>))

    (define (makeInt) (string->number tokenValue))

    (define (makeNorth) 'north)

    (define (makePaper <text>) (list 'paper <text>))

    (define (makeShield <style> <int>)
      (list 'shield (list '@ <style>) <int>))

    (define (makeSouth) 'south)

    (define (makeStop) '(stop))

    (define (makeString) tokenValue)

    ; FIXME: should strip outer double quotes

    (define (makeStyle <string>) (list 'style <string>))

    ; FIXME: should strip whitespace from either side.

    (define (makeTreasure <style> <int>)
      (list 'treasure (list '@ <style>) <int>))

    (define (makeUp) 'up)

    (define (makeWeapon <style> <int>)
      (list 'weapon (list '@ <style>) <int>))

    (define (makeWest) 'west)

    (define (makeWord) tokenValue)

    (define (makeWordText <word> <text>)
      (string-append <word>
                    (if (string=? <text> "") "" " ")
                    <text>))

    (define (makeWrite <text>) (list 'write <text>))
  
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    ;
    ; Error procedure called by the parser.
    ;
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
    (define (parse-error nonterminal expected-terminals)
      (let* ((culprit (next-token))
             (culprit-as-string (symbol->string culprit))
             (culprit-as-string
              (if (memq culprit expected-terminals)
                  (string-append "illegal " culprit-as-string)
                  culprit-as-string))
             (msg (string-append
                   "Syntax error while parsing "
                   (symbol->string nonterminal)
                   (string #\newline)
                   "  Encountered "
                   culprit-as-string
                   " while expecting "
                   (string-append
                    (string #\newline)
                    "  "
                    (apply string-append
                           (map (lambda (terminal)
                                  (string-append " "
                                                 (symbol->string terminal)))
                                expected-terminals)))
                   (string #\newline))))
        (error-return (list 'error msg))))

    (define error-return (lambda (x) x)) ; assigned below

    (call-with-current-continuation
     (lambda (return)
       (set! error-return return)
       (parse-message)))))

)


(library (local choose-randomly)
  (export debugging
          choose-randomly
          the-usual-random-number-generator
          max-castle-height
          max-castle-width
          max-castle-depth)
  (import (rnrs)
          (primitives random                   ; FIXME: Larceny-specific
                      current-seconds))

  ;; Set to true for console output.

  (define debugging #t)

  ;; No more than this many levels.

  (define max-castle-height 4)

  ;; No more than this many rooms from east to west.

  (define max-castle-width 20)

  ;; No more than this many rooms from north to south.

  (define max-castle-depth 20)

  ;; Given two arguments:
  ;;   a non-empty vector of procedures that take a random
  ;;       number generator as their only argument
  ;;   a random number generator
  ;;
  ;; Selects a random procedure from the vector and calls
  ;; it on the random number generator

  (define (choose-randomly procs rng)
    (let* ((n (vector-length procs))
           (i (mod (rng) n)))
      ((vector-ref procs i) rng)))

  ;; FIXME: this is Larceny-specific
  ;;
  ;; For deterministic random number generation,
  ;; replace the calls to (current-seconds) with
  ;; some specific integer.

  (define rng-range (mod (current-seconds) 9999999))
  (define rng-offset (mod (current-seconds) 1000000))

  (define (the-usual-random-number-generator)
    (+ (random rng-range) rng-offset))

  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; State module for CS U670 semester project.
;;;
;;; Prototype.
;;;
;;; The immutable state consists of the castle: its entrances
;;; and exits (gates), its rooms, and permanent characteristics
;;; of its gates and rooms.
;;;
;;; The mutable state consists of the participants, other objects,
;;; and their states.
;;;
;;; For this prototype, the state amounts to a maze plus the
;;; location of one player who is trying to find its way out
;;; of the maze.
;;;
;;; <castle>          ::=  ( <location> ... )
;;; <location>        ::=  record[ <id>
;;;                                <description>
;;;                                <neighbors>
;;;                                <characters>
;;;                                <items>]
;;; <description>     ::=  ( <location-type> <characteristic> ... )
;;; <location-type>   ::=  gate  |  gatehouse  |  yard
;;;                     |  hall  |  chapel
;;;                     |  keep  |  dungeon  |  oubliette
;;;                     |  kitchen  |  buttery  |  pantry
;;;                     |  storeroom  |  wardrobe
;;;                     |  bedchamber  |  bower  |  gallery
;;;                     |  bathroom  |  garderobe
;;; <characteristic>  ::=  <intrinsic>  |  <extrinsic>
;;; <intrinsic>       ::=  (stone)  |  (whitewashed)  |  (wainscoted)
;;;                     |  (painted <color>)
;;;                     |  (rug <color>)  |  (straw-floor)  |  (bare-floor)
;;;                     |  (tapestry <wall> <color>)
;;;                     |  (fireplace <wall>)
;;;                     |  (built <year>)
;;; <extrinsic>       ::=  (slot-window <wall>)  |  (arch-window <wall>)
;;;                     |  (arched-door <wall>)  |  (rectangular-door <wall>)
;;;                     |  (stair <up/down>)
;;; <color>           ::=  brown  |  gold  |  purple  |  green
;;;                     |  red  |  yellow  |  blue
;;; <year>            ::=  <integer>
;;; <wall>            ::=  north  |  south  |  east  | west
;;; <up/down>         ::=  up  |  down
;;; <direction>       ::=  <up/down>  |  <wall>
;;; <neighbors>       ::=  ( (<direction> . <location>) ... )
;;; <characters>      ::=  ( <character> ... )
;;; <items>           ::=  ( <item> ... )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Characters.
;;;
;;; A character is represented by a record with
;;;     an immutable species, a symbol
;;;     an immutable description, a string
;;;     a mutable health, a number (0 is nominal, -inf.0 is dead)
;;;     a mutable location
;;;     a mutable list of items
;;;     a mutable status, a symbol
;;;     an immutable input port (or #f)
;;;     an immutable output port (or #f)
;;;
;;; The status of a character can be any one of:
;;;     generated
;;;     player
;;;     deranged
;;;     deceased
;;;     retired
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(library (local characters)
  (export make-player
          make-character
          character?
          character-species
          character-description
          character-health
          character-health-set!
          character-location
          character-location-set!
          character-items
          character-items-set!
          character-status
          character-status-set!
          character-input-port
          character-output-port
          for-each-character)
  (import (rnrs base)
          (err5rs records syntactic))

  (define (make-player species description loc status iport oport)
    (let ((c (make-raw-character species
                                 description
                                 0
                                 loc
                                 '()
                                 status
                                 iport
                                 oport)))
      (set! all-characters (cons c all-characters))
      c))

  (define (make-character species description loc)
    (make-player species description loc 'generated #f #f))

  (define-record-type character
    make-raw-character
    character?
    species
    description
    (health)
    (location)
    (items)
    (status)
    input-port
    output-port)

  (define (for-each-character f)
    (for-each f all-characters))

  ;; List of all characters that have been created.

  (define all-characters '())

  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Items
;;;
;;; An item is represented by a record.  It
;;;     has a mutable location (which may instead be a character)
;;;
;;; There are various kinds of items:
;;;     frog
;;;     paper
;;;         has mutable text
;;;     treasure
;;;         has immutable style and mutable value
;;;     shield
;;;         has immutable style and mutable value
;;;     weapon
;;;         has immutable style and mutable value
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(library (local items)
  (export item? item-kind item-location item-location-set!
          make-frog frog?
          make-paper paper? paper-text paper-text-set!
          make-treasure treasure?
          treasure-style treasure-value treasure-value-set!
          make-shield shield?
          shield-style shield-value shield-value-set!
          make-weapon weapon?
          weapon-style weapon-value weapon-value-set!
          for-each-item)
  (import (rnrs base)
          (err5rs records syntactic))

  (define-record-type item #f item? (location))

  (define (item-kind item)
    (cond ((frog? item)
           'frog)
          ((paper? item)
           'paper)
          ((treasure? item)
           'treasure)
          ((shield? item)
           'shield)
          ((weapon? item)
           'weapon)
          (else
           'error)))

  (define-record-type (frog item) make-raw-frog frog?)

  (define-record-type (paper item) make-raw-paper paper? (text))

  (define-record-type (treasure item)
    make-raw-treasure treasure? style (value))

  (define-record-type (shield item)
    make-raw-shield shield? style (value))

  (define-record-type (weapon item)
    make-raw-weapon weapon? style (value))

  ;; make-maker mixes maintenance of the global list of items
  ;; with the raw maker

  (define (make-maker raw-maker)
    (lambda args
      (let ((x (apply raw-maker args)))
        (set! all-items (cons x all-items))
        x)))

  (define make-frog     (make-maker make-raw-frog))
  (define make-paper    (make-maker make-raw-paper))
  (define make-treasure (make-maker make-raw-treasure))
  (define make-shield   (make-maker make-raw-shield))
  (define make-weapon   (make-maker make-raw-weapon))

  (define (for-each-item f)
    (for-each f all-items))

  ;; List of all items that have been created.

  (define all-items '())

  )

(library (local locations)
  (export make-location
          location?
          location-id
          location-description
          location-neighbors
          location-description-set!
          location-neighbors-set!
          location-characters
          location-characters-set!
          location-items
          location-items-set!
          characteristic->string)
  (import (rnrs base)
          (err5rs records procedural))

  (define location-rtd
    (make-rtd 'location
              '#((immutable id) description neighbors characters items)))

  (define make-raw-location (rtd-constructor location-rtd))

  (define (make-location id description neighbors)
    (make-raw-location id description neighbors '() '()))

  (define location? (rtd-predicate location-rtd))

  (define location-id (rtd-accessor location-rtd 'id))

  (define location-description (rtd-accessor location-rtd 'description))

  (define location-description-set! (rtd-mutator location-rtd 'description))

  (define location-neighbors (rtd-accessor location-rtd 'neighbors))

  (define location-neighbors-set! (rtd-mutator location-rtd 'neighbors))

  (define location-characters (rtd-accessor location-rtd 'characters))

  (define location-characters-set! (rtd-mutator location-rtd 'characters))

  (define location-items (rtd-accessor location-rtd 'items))

  (define location-items-set! (rtd-mutator location-rtd 'items))

  (define (characteristic->string characteristic)
    (cond ((symbol? characteristic)
           (symbol->string characteristic))
          ((number? characteristic)
           (number->string characteristic))
          ((pair? characteristic)
           (if (null? (cdr characteristic))
               (characteristic->string (car characteristic))
               (string-append (characteristic->string (car characteristic))
                              " "
                              (characteristic->string (cdr characteristic)))))
          (else
           (assertion-violation 'characteristic->string
                                "weird characteristic"
                                characteristic)
           "...")))

  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Location generators.
;;;
;;; A location generator is a procedure that takes a random
;;; number generator as its argument and returns a <location>.
;;; Location generators are defined using characteristic
;;; generators, et cetera.
;;;
;;; There are 2*2*2*8*29*5*9 = 83520 combinations of
;;; intrinsic characteristics, not counting the year built.
;;; That's enough so we can choose intrinsic characteristics
;;; at random, adding the year built only when two different
;;; rooms have the same <location-type> and other characteristics.

(library (local location-generators)
  (export the-usual-location-generator)
  (import (rnrs)
          (local choose-randomly)
          (local locations))

  (define (the-usual-location-generator rng)
    (choose-randomly location-generators rng))

  (define (location-generator location-type intrinsics-generator)
    (lambda (rng)
      (let* ((id (id-generator))
             (type location-type)
             (intrinsics (intrinsics-generator rng)))
        (make-location id (cons type intrinsics) '()))))

  (define id-generator
    (let ((id 1))
      (lambda ()
        (set! id (+ id 1))
        id)))

  (define (random-color rng)
    (let* ((colors '#(brown gold purple green red yellow blue))
           (i (mod (rng) (vector-length colors))))
      (vector-ref colors i)))

  (define (random-wall rng)
    (let* ((walls '#(north east south west))
           (i (mod (rng) (vector-length walls))))
      (vector-ref walls i)))

  (define (the-usual-walls-generator rng)
    (let* ((t1 (if (even? (rng)) '() '((stone))))
           (t2 (if (even? (rng)) '() '((whitewashed))))
           (t3 (if (even? (rng)) '() '((wainscoted))))
           (t4 (if (even? (rng)) '() `((painted ,(random-color rng)))))
           (t5 (if (even? (rng)) '() `((tapestry ,(random-wall rng)
                                                 ,(random-color rng)))))
           (t6 (if (even? (rng)) '() `((fireplace ,(random-wall rng))))))
      (append t1 t2 t3 t4 t5 t6)))

  (define (the-usual-floor-generator rng)
    (case (mod (rng) 3)
     ((0) '((bare-floor)))
     ((1) '((straw-floor)))
     (else
      `((rug ,(random-color rng))))))

  (define (the-usual-intrinsics-generator rng)
    (let* ((walls (the-usual-walls-generator rng))
           (floor (the-usual-floor-generator rng)))
      (append walls floor)))

  (define location-generators
    (vector
     (location-generator 'hall       the-usual-intrinsics-generator)
     (location-generator 'chapel     the-usual-intrinsics-generator)
     (location-generator 'keep       the-usual-intrinsics-generator)
     (location-generator 'dungeon    the-usual-intrinsics-generator)
     (location-generator 'oubliette  the-usual-intrinsics-generator)
     (location-generator 'kitchen    the-usual-intrinsics-generator)
     (location-generator 'buttery    the-usual-intrinsics-generator)
     (location-generator 'pantry     the-usual-intrinsics-generator)
     (location-generator 'storeroom  the-usual-intrinsics-generator)
     (location-generator 'wardrobe   the-usual-intrinsics-generator)
     (location-generator 'bedchamber the-usual-intrinsics-generator)
     (location-generator 'bower      the-usual-intrinsics-generator)
     (location-generator 'gallery    the-usual-intrinsics-generator)
     (location-generator 'bathroom   the-usual-intrinsics-generator)
     (location-generator 'garderobe  the-usual-intrinsics-generator)))

  )


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Initialization.
;;;
;;; Initialization of the castle is determined by
;;; a random number generator that takes no arguments
;;; and returns non-negative integers.
;;;
;;; Initialization proceeds as follows:
;;;
;;; Choose the height of the castle (>= 1).
;;; Choose the north-south and east-west dimensions of the castle (>= 1).
;;; Choose the rooms of the castle.
;;; Choose neighbors for each room.
;;; Choose characteristics for each room.
;;; Verify that every room is reachable from the outside.
;;;   Add neighbors as necessary.
;;; Verify that every room has a distinct description.
;;;   Add characteristics as necessary.
;;; Create and place characters.
;;; Create and place items.
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(library (local initialization)
  (export the-castle
          the-outside
          the-frog
          reachable-rooms
          unreachable-rooms
          choose-reachable-room
          choose-entry-room)
  (import (rnrs)
          (local choose-randomly)
          (local locations)
          (local location-generators)
          (local characters)
          (local items))

  (define the-rng the-usual-random-number-generator)

  ;; Choose the height and dimensions of the castle.

  (define the-height (+ 1 (mod (the-rng) max-castle-height)))

  (define the-width (+ 1 (mod (the-rng) max-castle-width)))

  (define the-depth (+ 1 (mod (the-rng) max-castle-depth)))

  (define the-outside
    (make-location 0 (list 'yard) '()))

  ;; FIXME: Scheme should have a standard array package.

  (define (make-array3 i j k)
    (vector-map (lambda (x) (make-array2 j k))
                (make-vector i)))

  (define (make-array2 j k)
    (vector-map (lambda (x) (make-vector k #f))
                (make-vector j)))

  (define the-rooms (make-array3 the-height the-depth the-width))

  ;; (room i j k) returns the room at level i, row j, column k
  ;; If i, j, or k is out of range, returns the-outside.

  (define (room i j k)
    (if (and (< -1 i the-height)
             (< -1 j the-depth)
             (< -1 k the-width))
        (vector-ref (vector-ref (vector-ref the-rooms i)
                                j)
                    k)
        the-outside))

  ;; (room-set! i j k r) stores r at level i, row j, column k

  (define (room-set! i j k r)
    (vector-set! (vector-ref (vector-ref the-rooms i)
                             j)
                 k
                 r))

  ;; (for-each-room proc)
  ;; calls proc on every level i, row j, column k, and (room i j k)

  (define (for-each-room proc)
    (do ((i 0 (+ i 1)))
        ((= i the-height))
      (do ((j 0 (+ j 1)))
          ((= j the-depth))
        (do ((k 0 (+ k 1)))
            ((= k the-width))
          (proc i j k (room i j k))))))    

  ;; Choose the rooms of the castle.

  (define ignored1
    (for-each-room
     (lambda (i j k ignored)
       (room-set! i j k (the-usual-location-generator the-rng)))))

  ;; Choose neighbors for each room.
  ;; First choose neighbors in one direction, then patch
  ;; in the other direction.

  (define ignored2
    (for-each-room
     (lambda (i j k r0)
       (let ((directions '())
             (neighbors '()))
         (define (maybe-add-neighbor! direction i j k)
           (if (and (< -1 i the-height)
                    (zero? (mod (the-rng) 3)))
               (let ((r (room i j k)))
                 (if (not (memv r neighbors))
                     (begin (set! directions (cons direction directions))
                            (set! neighbors (cons r neighbors)))))))
         (maybe-add-neighbor! 'down (- i 1) j k)
         (maybe-add-neighbor! 'up (+ i 1) j k)
         (maybe-add-neighbor! 'north i (- j 1) k)
         (maybe-add-neighbor! 'south i (+ j 1) k)
         (maybe-add-neighbor! 'west i j (- k 1))
         (maybe-add-neighbor! 'east i j (+ k 1))
         (location-neighbors-set! r0 (map cons directions neighbors))))))

  (define ignored3
    (for-each-room
     (lambda (i j k r0)
       (define (opposite-direction dir)
         (case dir
          ((up) 'down)
          ((down) 'up)
          ((north) 'south)
          ((south) 'north)
          ((east) 'west)
          ((west) 'east)
          (else (assert #f))))
       (let ((neighbors0 (location-neighbors r0)))
         (for-each (lambda (direction neighbor)
                     (if (not (eqv? neighbor the-outside))
                         (let* ((neighbors (location-neighbors neighbor))
                                (opposite (opposite-direction direction))
                                (x (cons opposite r0)))
                           (if (not (member x neighbors))
                               (location-neighbors-set!
                                neighbor
                                (cons x neighbors))))))
                   (map car neighbors0)
                   (map cdr neighbors0))))))

  ;; Choose characteristics for each room.
  ;; Verify that every room is reachable from the outside.
  ;;   Add neighbors as necessary.
  ;;
  ;; FIXME: not done; some rooms may not be reachable.

  ;; Returns a list of the reachable rooms.

  (define (reachable-rooms)
    (let ((reachable (make-hashtable location-id eqv?)))
      (define (compute-reachable!)
        (let ((n (hashtable-size reachable)))
          (for-each-room
           (lambda (i j k r)
             (let* ((neighbors (location-neighbors r))
                    (locations (map cdr neighbors)))
               (for-each (lambda (loc)
                           (if (hashtable-contains? reachable loc)
                               (hashtable-set! reachable r #t)))
                         locations)
               (if (hashtable-contains? reachable r)
                   (for-each (lambda (loc)
                               (hashtable-set! reachable loc #t))
                             locations)))))
          (if (< n (hashtable-size reachable))
              (compute-reachable!))))
      (hashtable-set! reachable the-outside #t)
      (compute-reachable!)
      (vector->list (hashtable-keys reachable))))

  ;; Returns a list of the unreachable rooms.

  (define (unreachable-rooms)
    (let ((reachable (make-hashtable location-id eqv?))
          (unreachable (make-hashtable location-id eqv?)))
      (for-each (lambda (r) (hashtable-set! reachable r #t))
                (reachable-rooms))
      (for-each-room (lambda (i j k r)
                       (if (not (hashtable-contains? reachable r))
                           (hashtable-set! unreachable r #t))))
      (vector->list (hashtable-keys unreachable))))

  ;; Returns a randomly selected reachable room.

  (define (choose-reachable-room)
    (let* ((reachable (remv the-outside (reachable-rooms)))
           (n (length reachable))
           (i (mod (the-rng) n)))
      (list-ref reachable i)))

  ;; Returns a randomly selected room that's adjacent to the outside.

  (define (choose-entry-room)
    (let* ((reachable (remv the-outside (reachable-rooms)))
           (reachable (filter (lambda (r)
                                (memv the-outside
                                      (map cdr (location-neighbors r))))
                              reachable))
           (n (length reachable))
           (i (mod (the-rng) n)))
      (list-ref reachable i)))

  ;; Verify that every room has a distinct description.
  ;;   Add characteristics as necessary.

  (define (canonical-description r)
    (let* ((characteristics (location-description r))
           (characteristics (map characteristic->string characteristics))
           (characteristics (list-sort string<? characteristics)))
      (apply string-append characteristics)))

  (define ignored4
    (let ((year 8000)
          (ht (make-hashtable string-hash string=?)))
      (for-each-room
       (lambda (i j k r)
         (let ((description (canonical-description r)))
           (if (hashtable-contains? ht description)
               (let ((description (location-description r)))
                 (set! year (+ year 1))
                 (location-description-set!
                  r
                  (cons (car description)
                        (cons (list 'built year)
                              (cdr description))))))
           (hashtable-set! ht (canonical-description r) r))))))

  ;; Create and place characters.
  ;; FIXME:  Just the player for now.

  (define ignored5
    (let* ((room (choose-reachable-room))
           (occupants (location-characters room))
           (player (make-player 'peon
                                "looks like Tom Cruise"
                                room
                                'player
                                (current-input-port)
                                (current-output-port))))
      (character-location-set! player room)
      (location-characters-set! room (cons player occupants))))

  ;; Create and place items
  ;; FIXME:  Just the frog for now.

  ;; The one and only enchanted frog.

  (define the-frog
    (let* ((room (choose-reachable-room))
           (items (location-items room))
           (frog (make-frog room)))
      (location-items-set! room (cons frog items))
      frog))

  (define all-rooms
    (let ((all-rooms '()))
      (for-each-room (lambda (i j k room)
                       (set! all-rooms (cons room all-rooms))))
      all-rooms))

  (define the-castle (cons the-outside all-rooms))

  )

(library (local xml out)
  (export write-outside write-room write-gameover)
  (import (rnrs)
          (local choose-randomly)
          (local locations)
          (local characters)
          (local items))

  (define the-rng the-usual-random-number-generator)

  (define console
    (transcoded-port (standard-output-port)
                     (make-transcoder (utf-8-codec))))

  ;; Writes an XML <outside></outside> element to an output port.
  ;; If debugging is true, a description is also written to the
  ;; console.

  (define (write-outside out)
    (define (write-outside out)
      (newline out)
      (display "<outside>" out)
      (newline out)
      (display "</outside>" out)
      (newline out)
      (newline out))
    (write-outside out)
    (if debugging
        (write-outside console)))

  ;; Writes an XML description of the room to an output port.
  ;; Excludes the description of the player who observes the room.
  ;; If debugging is true, a description is also written to the
  ;; console.

  (define (write-room r player out)
    (let* ((desc (location-description r))
           (exits (map car (location-neighbors r)))
           (type (car desc))
           (characteristics (cdr desc))
           (characters (remv player (location-characters r)))
           (items (location-items r))
           (elements (cons (list 'purpose type)
                           (cons (cons 'exits exits)
                                 (map (lambda (x)
                                        (list 'characteristic x))
                                      characteristics))))
           (elements
            (list-sort (lambda (x y) (even? (the-rng)))
                       elements))
           (elements (append elements
                             (map (lambda (x) (list 'character x))
                                  characters)
                             (map (lambda (x) (list 'item x))
                                  items))))
      (if debugging
          (write-room-xml elements player console))
      (write-room-xml elements player out)))

  (define (write-room-xml elements player out)

    (define (write-element element)
      (case (car element)
       ((purpose)
        (write-line "  <purpose>")
        (write-line "    " (symbol->string (cadr element)))
        (write-line "  </purpose>"))
       ((characteristic)
        (write-line "  <characteristic>")
        (write-line "    "
                    (characteristic->string (cdr element)))
        (write-line "  </characteristic>"))
       ((exits)
        (write-line "  <exits>")
        (for-each (lambda (exit)
                    (write-line "    <exit>")
                    (write-line "      " exit)
                    (write-line "    </exit>"))
                  (cdr element))
        (write-line "  </exits>"))
       ((character)
        (write-line "  <character>")
        (write-line "    <species>")
        (write-line (string-append "      "
                                   (symbol->string
                                    (character-species (cadr element)))))
        (write-line "    </species>")
        (write-line "    <description>")
        (write-line (string-append "      "
                                   (character-description (cadr element))))
        (write-line "    </description>")
        (write-line "  </character>"))
       ((item)
        (write-line "  <item>")
        (case (item-kind (cadr element))
         ((frog)
          (write-line "    <frog>")
          (write-line "    </frog>"))
         ((paper)
          (write-line "    <paper>")
          (write-line (string-append "      " (paper-text (cadr element))))
          (write-line "    </paper>"))
         ((treasure)
          (write-line (string-append "    <treasure style=\""
                                     (treasure-style (cadr element))
                                     "\""))
          (write-line (number->string (treasure-value (cadr element))))
          (write-line "    </treasure>"))
         ((shield)
          (write-line (string-append "    <shield style=\""
                                     (shield-style (cadr element))
                                     "\""))
          (write-line (number->string (shield-value (cadr element))))
          (write-line "    </shield>"))
         ((weapon)
          (write-line (string-append "    <weapon style=\""
                                     (weapon-style (cadr element))
                                     "\""))
          (write-line (number->string (weapon-value (cadr element))))
          (write-line "    </weapon>"))
         (else
          (assertion-violation 'write-room-xml "weird item" element)))
        (write-line "  </item>"))
       (else
        (assertion-violation 'write-rooom-xml
                             "weird element"
                             element))))

    (define (write-line . strings)
      (for-each (lambda (s) (display s out))
                strings)
      (newline out))

    (write-line)
    (write-line "<room>")
    (for-each write-element elements)
    (write-line "</room>")
    (write-line))

  ;; Writes an XML description of the gameover message to standard output.
  ;; If debugging is true, the same description is also written to the
  ;; console.

  (define (write-gameover msg out)
      (if debugging
          (write-gameover-xml msg console))
      (write-gameover-xml msg out))

  (define (write-gameover-xml msg out)

    (define (write-line . strings)
      (for-each (lambda (s) (display s out))
                strings)
      (newline out))

    (write-line)
    (write-line "<gameover>")
    (write-line "  <outcome>")
    (write-line "    " msg)
    (write-line "  </outcome>")
    (write-line "</gameover>")
    (write-line))

  )
  
(library (local xml in)
  (export read-xml-message)
  (import (rnrs) (local parse-xml-message))

  ;; Reads an exit element, returning the specified exit.

  (define read-xml-message parse-xml-message)

  ;; FIXME: no longer used
  ;;
  ;; Given a string, returns the substring from which
  ;; surrounding whitespace has been removed.

  (define (trim-whitespace s)
    (define (trim-spaces chars)
      (cond ((null? chars) chars)
            ((char-whitespace? (car chars))
             (trim-spaces (cdr chars)))
            (else chars)))
    (list->string
     (trim-spaces (reverse (trim-spaces (reverse (string->list s)))))))

  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Assignment 5.
;;;
;;; Initialize the castle.
;;; Choose a reachable room.
;;; While the current room is not outside the castle:
;;;     Describe the current room.
;;;     Read an exit and take that exit.
;;; Write a gameover message.

(library (local game7)
  (export game7)
  (import (rnrs)
          (local parse-xml-message)
          (local locations)
          (local characters)
          (local items)
          (local initialization)
          (local xml out)
          (local xml in))

  ;; Number of moves so far.

  (define moves -1)

  (define (game7)

    (set! moves (+ moves 1))

    (let ((players 0))

      (for-each-character
       (lambda (player)
         (case (character-status player)
          ((player)
           (set! players (+ players 1))
           (let* ((in (character-input-port player))
                  (out (character-output-port player))
                  (health (character-health player))
                  (the-current-room (character-location player))
                  (held-items (character-items player))
                  (room-items (location-items the-current-room)))

             (if (eqv? the-current-room the-outside)

                 (let ((frog-location (item-location the-frog)))

                   (if (or (eqv? frog-location the-outside)
                           (memv the-frog held-items))

                       (retire! player #t out)

                       (begin (write-outside out)
                              (let ((msg (parse-xml-message in)))
                                (case (car msg)
                                 ((stop)
                                  (retire! player #f out))
                                 ((enter)
                                  (character-location-set!
                                   player
                                   (choose-entry-room)))
                                 (else
                                  (institutionalize! player
                                                     (car msg)
                                                     out)))))))

                 (begin (write-room the-current-room player out)
                        (let ((msg (parse-xml-message in)))
                          (case (car msg)
                           ((exit)
                            (let* ((neighbors
                                    (location-neighbors the-current-room))
                                   (probe (assq (cadr msg) neighbors)))
                              (if probe
                                  (character-location-set! player (cdr probe))
                                  (institutionalize! player (cadr msg) out))))
                           ((grasp)
                            (if (or (null? room-items)
                                    (not (null? held-items)))
                                (institutionalize! player 'grasp out)
                                (let ((item (car room-items))) ;FIXME
                                  (character-items-set! player (list item))
                                  (location-items-set! the-current-room
                                                       (cdr room-items))
                                  (item-location-set! item player))))
                           ((drop)
                            (if (null? held-items)
                                (institutionalize! player 'drop out)
                                (begin
                                 (character-items-set! player '())
                                 (location-items-set! the-current-room
                                                      (cons (car held-items)
                                                            room-items))
                                 (item-location-set! (car held-items)
                                                     the-current-room))))
                           ; FIXME: write and assault not implemented yet
                           (else
                            (institutionalize! player (car msg) out)))))))))))

      (if (> players 0)
          (game7))))

  ;; Marks a player as retired and writes a gameover message.

  (define (retire! player frog-rescued? out)
    (character-status-set! player 'retired)
    (write-gameover (make-congratulations frog-rescued?) out))

  ;; Marks a player as deranged and writes a gameover message.

  (define (institutionalize! player thing out)
    (character-status-set! player 'deranged)
    (write-gameover (make-lossage thing) out))

  ;; Returns a congratulatory message.

  (define (make-congratulations . rest)
    (let ((phrase (if (and (not (null? rest))
                           (car rest))
                      "You rescued the frog"
                      "You escaped from the castle")))
      (string-append "Congratulations!  "
                     phrase
                     " in "
                     (number->string moves)
                     " moves.")))

  ;; Returns an error message.

  (define (make-lossage reason)
    (string-append "You lose after "
                   (number->string moves)
                   " moves because "
                   (symbol->string reason)
                   " doesn't make sense here."))

  )



(import (rnrs)
        (local initialization)
        (local game7))

;(write (list (length the-castle)
;             (length (reachable-rooms))
;             (length (unreachable-rooms))))
;(newline)

;(for-each write-room the-castle)

(game7)

(exit 0)
