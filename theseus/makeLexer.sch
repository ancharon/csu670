; Copyright 2008 William D Clinger
;
; Script for generating state machine and parser to use in referee.
;
; Requires:
;     Larceny.
;        (To modify for other systems, see FIXME comments.)
;     LexGen and ParseGen
;        ( http://www.ccs.neu.edu/home/will/Research/SW2006/*.tar.gz )
;     refereeTokens.sch (regular syntax of Larceny)
;     referee.pg (context-free syntax of Larceny)
;
; Creates:
;     dfaReferee.sch
;     parserReferee.sch
;     tablesReferee
;
; The definitions of state0 through stateN must be extracted
; by hand from dfaReferee.sch and copied into reader.sch.
;
; The entire contents of parserReferee.sch must be copied into
; referee.sch.
;

; Change these path names for your system.

(define input:lexgen "/proj/will/LarcenyDev/lib/LexGen/loadlexgen.sch")
(define input:parsegen "/proj/will/LarcenyDev/lib/ParseGen/loadparsegen.sch")

(define input:regexps "refereeTokens.sch")
(define input:grammar "referee.pg")

(define output:dfa "dfaReferee.sch")
(define output:parser "parserReferee.sch")
(define output:tables "tablesReferee")

; ParseGen must be loaded before LexGen, I think.

(load input:parsegen)

(load input:lexgen)

(load input:regexps)

(display "Generating minimal DFA.")
(newline)

(let ((x (time (generate-scheme-lexer scheme_terminals))))
  (call-with-output-file
   output:dfa
   (lambda (p)
     (pretty-print x p))))

(display "Generating parser.")
(newline)

(generate-scheme input:grammar output:parser output:tables)
