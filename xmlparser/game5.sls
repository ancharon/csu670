;;; This file contains ERR5RS/R6RS libraries followed by
;;; an ERR5RS/R6RS top-level program.

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
  
  ;;(define rng-range (mod 26 9999999))
  ;;(define rng-offset (mod 26 1000000))
  
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
;;; <location>        ::=  record[ <id> <description> <neighbors> ]
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

(library (local locations)
  (export make-location
          location?
          location-id
          location-description
          location-neighbors
          location-description-set!
          location-neighbors-set!
          characteristic->string)
  (import (rnrs base)
          (err5rs records procedural))

  (define location-rtd
    (make-rtd 'location
              '#((immutable id) description neighbors)))

  (define make-location (rtd-constructor location-rtd))

  (define location? (rtd-predicate location-rtd))

  (define location-id (rtd-accessor location-rtd 'id))

  (define location-description (rtd-accessor location-rtd 'description))

  (define location-description-set! (rtd-mutator location-rtd 'description))

  (define location-neighbors (rtd-accessor location-rtd 'neighbors))

  (define location-neighbors-set! (rtd-mutator location-rtd 'neighbors))

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
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(library (local initialization)
  (export the-castle
          the-outside
          reachable-rooms
          unreachable-rooms)
  (import (rnrs)
          (local choose-randomly)
          (local locations)
          (local location-generators))

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

  (define all-rooms
    (let ((all-rooms '()))
      (for-each-room (lambda (i j k room)
                       (set! all-rooms (cons room all-rooms))))
      all-rooms))

  (define the-castle (cons the-outside all-rooms))

  )

(library (local xml out)
  (export write-room write-gameover)
  (import (rnrs)
          (local choose-randomly)
          (local locations))

  (define the-rng the-usual-random-number-generator)

  (define console
    (transcoded-port (standard-output-port)
                     (make-transcoder (utf-8-codec))))

  ;; Writes an XML description of the room to standard output.
  ;; If debugging is true, a description is also written to the
  ;; console.

  (define (write-room r)
    (let* ((desc (location-description r))
           (exits (map car (location-neighbors r)))
           (type (car desc))
           (characteristics (cdr desc))
           (elements (cons (list 'purpose type)
                           (cons (cons 'exits exits)
                                 (map (lambda (x) (list 'characteristic x))
                                      characteristics))))
           (elements
            (list-sort (lambda (x y) (even? (the-rng)))
                       elements)))
      (if debugging
          (write-room-xml elements console))
      (write-room-xml elements (current-output-port))))

  (define (write-room-xml elements out)

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

  (define (write-gameover msg)
      (if debugging
          (write-gameover-xml msg console))
      (write-gameover-xml msg (current-output-port)))

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
  (export read-exit)
  (import (rnrs))

  ;; Reads from the given input until the specified character
  ;; is seen.  Does not consume that character.  Returns a
  ;; string of all characters read up to that character.

  (define (read-until c0 in)
    (define (loop chars)
      (let ((c (peek-char in)))
        (cond ((or (eof-object? c)
                   (char=? c c0))
               (list->string (reverse chars)))
              (else
               (read-char in)
               (loop (cons c chars))))))
    (loop '()))

  ;; Reads an exit element, returning the specified exit.

  (define (read-exit)
    (let* ((x1 (read-until #\> (current-input-port)))
           (c1 (read-char (current-input-port)))
           (x2 (read-until #\< (current-input-port)))
           (x3 (read-until #\> (current-input-port)))
           (c3 (read-char (current-input-port))))
      (if (and (string? x1)
               (char? c1)
               (string? x2)
               (string? x3)
               (char? c3)
               (string=? (trim-whitespace x1) "<exit")
               (char=? c1 #\>)
               (string=? (trim-whitespace x3) "</exit")
               (char=? c3 #\>))
          (let ((x (trim-whitespace x2)))
            (cond ((string=? x "up") 'up)
                  ((string=? x "down") 'down)
                  ((string=? x "north") 'north)
                  ((string=? x "south") 'south)
                  ((string=? x "east") 'east)
                  ((string=? x "west") 'west)
                  (else
                   'error)))
          'error)))

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

(library (local game5)
  (export game5)
  (import (rnrs)
          (local locations)
          (local initialization)
          (local xml out)
          (local xml in))

  ;; Number of moves so far.

  (define moves 0)

  ;; The current room.

  (define the-current-room
    (let* ((reachable (reachable-rooms))
           (n (length reachable)))
      (list-ref reachable (div n 2))))

  (define (game5)
    (if (eqv? the-current-room the-outside)
        (write-gameover (make-congratulations))
        (let ((neighbors (location-neighbors the-current-room)))
          (write-room the-current-room)
          (let* ((direction (read-exit))
                 (probe (assq direction neighbors)))
            (set! moves (+ moves 1))
            (if probe
                (begin (set! the-current-room (cdr probe))
                       (game5))
                (write-gameover (make-lossage direction)))))))

  ;; Returns a congratulatory message.

  (define (make-congratulations)
    (string-append "Congratulations!  "
                   "You escaped from the castle in "
                   (number->string moves)
                   " moves."))

  ;; Returns an error message.

  (define (make-lossage direction)
    (string-append "You lose after "
                   (number->string moves)
                   " moves because you made an illegal move."))

  )



(import (rnrs)
        (local initialization)
        (local game5))

;(write (list (length the-castle)
;             (length (reachable-rooms))
;             (length (unreachable-rooms))))
;(newline)

;(for-each write-room the-castle)

(game5)

(exit 0)
