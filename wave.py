"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class are to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    # Attribute _direction: the current direction the aliens should move in
    # Invariant: _direction is a string of "left" or "right"

    #Attribute _lastSpace: stores whether or not the space bar was pressed last frame
    #Invariant: _lastSpace is a bool

    #Attribute _boltSpeed: the number of steps until the aliens must fire
    #Invariant: _boltSpeed a float >= 0

    #Attribute _steps: the number of steps taken by the aliens
    #Invariant: _steps a float >= 0

    # Attribute _animator: The animation coroutine for the ship.
    # Invariant: _animator is either None or a coroutine

    # Attribute _alienAnimator: The animation coroutine for Aliens.
    # Invariant: _alienAnimator is either None or a coroutine

    # Attribute _index1: the row of the alien currently hit by a bolt.
    # Invariant: _index1 is an int >= 0

    # Attribute _index2: the posistion in the row of the alien currently hit by a bolt.
    # Invariant: _index2 is an int >= 0

    # Attribute _outcome: the outcome of the game.
    # Invariant: _outcome is either None or a string of "win" or "lose"

    # Attribute _mute: the number of unique times "m" has been pressed
    # Invariant: _mute is an int >=0

    # Attribute _sounds: the list of sounds used in the game
    # Invariant: _sounds is a list of Sound objects

    #Attribute _lastM: stores whether or not the "m" was pressed in the last frame
    #Invariant: _lastM is a bool

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def getShip(self):
        """
        A getter for self._ship
        """
        return self._ship

    def getOutcome(self):
        return self._outcome

    def getLives(self):
        return self._lives

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializes the wave
        """
        self._aliens = []
        self._fillAliens()
        self._bolts = []
        self._ship = Ship()
        self._dline = GPath(points = [0, DEFENSE_LINE, GAME_WIDTH,DEFENSE_LINE], linewidth = 1.1, linecolor = "black")
        self._lives = 3
        self._time = 0
        self._direction = "right"
        self._boltSpeed = random.randrange(BOLT_RATE)
        self._steps = 0
        self._animator = None
        self._alienAnimator = None
        self._index1 = 0
        self._index2 = 0
        self._outcome = None
        self._mute = 0
        self._sounds = [Sound('pew2.wav'), Sound('blast3.wav'), Sound('blast2.wav'),
                        Sound('blast1.wav'), Sound('pop1.wav')]

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        """
        Animates a single frame to move the ships, aliens, and laser bolts.

        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float.

        Parameter input: the given input.
        Precondition: an instance of GInput.
        """
        #Move and animate ship
        if self._animator is not None:
            self.runShipAnimator(dt)
        else:
            self._ship.moveShip(input)
            self._createPlayerBolt(input)
            self._moveBolt()

        if self._alienAnimator is not None:
            self.runAlienAnimator(dt)

        self._moveAlienWave(dt)

        self._createAlienBolt(dt)
        self._destroyAliens()
        self._destroyShip()
        self._checkOutcome()
        self._muteSounds(input)

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the ships aliens, deffensive line and bolts.

        Parameter: The view window
        Precondition: view is a GView.
        """
        #draw aliens
        for rows in self._aliens:
            for alien in rows:
                if alien != None:
                    alien.draw(view)

        #draw ships
        if self._ship != None:
            self._ship.draw(view)

        #draw defense line
        self._dline.draw(view)

        #draw bolts
        if self._bolts != []:
            for bolt in self._bolts:
                bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
    def _fillAliens(self):
        """
        Helper function for the wave's initializator that fills the self._aliens
        with a 2d list of aliens
        """
        yNext = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_HEIGHT/2)
        fileNum = 0
        currentRow = 0

        for x in range(ALIEN_ROWS):
            xNext = ALIEN_H_SEP + (ALIEN_WIDTH/2)

            #change image every time the current row is divi
            currentRow = currentRow + 1
            if fileNum == 3:
                fileNum = 0

            #create variable to store row of aliens
            row = []

            for x in range(ALIENS_IN_ROW):
                row.append(Alien(xNext, yNext, fileNum))
                xNext = xNext + ALIEN_WIDTH + ALIEN_H_SEP
            yNext = yNext - ALIEN_HEIGHT - ALIEN_V_SEP

            self._aliens.append(row)

            if (currentRow % 2) == 0:
                fileNum = fileNum +1

    #HELPER METHODS TO MOVE THE WAVE OF ALIENS
    def _moveAlienWave(self, dt):
        """
        The central helper method that controls the overall movement of the Alien Wave.

        Parameter dt: The number of seconds since the last animation frame
        Precondition: dt is an number >= 0
        """
        if self._time <= ALIEN_SPEED:
            self._time += dt

        #move wave once the number of seconds past is bigger than ALIEN_SPEED
        if self._time > ALIEN_SPEED:

            self._steps += 1
            self._walkAliens()

            #move wave ALIEN_H_SEP from edge, the step before changing directions
            if self._direction == "switchLeft" or self._direction == "switchRight":
                self._moveWaveAcross(self._direction)
                #change self._direction so the wave can change directions in the next step.
                if self._direction == "switchLeft":
                    self._direction = "left"
                elif self._direction == "switchRight":
                    self._direction = "right"

            #move wave down when an alien reaches the edge
            elif self.alienAtEdge(self._direction) == True:
                self._moveWaveDown(self._direction)

            #move the wave left and right
            elif self._direction == "right" or self._direction == "left":
                    self._moveWaveAcross(self._direction)

            self._time = 0

    def _moveWaveAcross(self, direction):
        """
        Helper method that moves the wave of aliens left or right
        """
        for rows in self._aliens:
            for alien in rows:
                if alien != None:
                    alien.moveAlienAcross(direction)

    def _moveWaveDown(self, direction):
        """
        Helper method that moves the wave of aliens down
        """
        for rows in self._aliens:
            for alien in rows:
                if alien != None:
                    alien.moveAlienDown(direction)

        #change self._direction after the wave moves down, so the wave can take a
        #ALIEN_H_SEP step away from the edge before switching direction
        if direction == "right":
            self._direction = "switchLeft"
        elif direction == "left":
            self._direction = "switchRight"

    def alienAtEdge(self, direction):
        """
        Helper method that detects when an alien is at the right or left edge
        """
        #check each alien in row
        for rows in self._aliens:
            for alien in rows:
                #return true if there is an alien at the right edge
                if direction == "right":
                    if alien != None and alien.getX() + (ALIEN_WIDTH/2) >= GAME_WIDTH - ALIEN_H_SEP:
                        return True
                #return true if there is an alien at the right edge
                elif direction == "left":
                    if alien != None and alien.getX() - (ALIEN_WIDTH/2) < ALIEN_H_SEP:
                        return True
        return False

    #HELPER METHODS THAT CREATE AND MOVE BOLTS
    def _createPlayerBolt(self, input):
        """
        Helper that creates a player Bolt if the spacebar is pressed.
        Also ensures the player can only create a bolt if there is not another
        player bolt on the screen

        Parameter input: the given input.
        Precondition: an instance of GInput.
        """
        currentSpace = input.is_key_down('spacebar')

        playerBolts = 0
        for x in self._bolts:
            if x.isPlayerBolt() == True:
                playerBolts = playerBolts + 1

        #first makes sure there was no Bolt created the frame before
        if currentSpace == True and self._lastSpace == False:
            #then makes sure the player doesnt have a bolt on the screen
            if self._bolts == [] or playerBolts == 0:
                #creates bolt only if both are true
                self._bolts.append(Bolt(self._ship.getX(), self._ship.getY() + SHIP_HEIGHT, BOLT_SPEED))
                self._sounds[0].play()

        self._lastSpace = currentSpace

    def _moveBolt(self):
        """
        Helper method that moves both player and alien bolts. It also deletes
        both player and alien bolts out of view
        """
        #move bolt
        for bolt in self._bolts:
            bolt.setY( (bolt.getY() + bolt.getVelocity()) )

        # Delete bolts out of view
        x = 0
        while x < len(self._bolts):
            #delete player bolts out of view
            if (self._bolts[x].getY() - BOLT_HEIGHT/2) > GAME_HEIGHT:
                del self._bolts[x]
            #delete alien bolts out of view
            elif (self._bolts[x].getY() + BOLT_HEIGHT/2) < 0:
                del self._bolts[x]
            else:
                x += 1

    def _createAlienBolt(self, dt):
        """
        Creates alien bolt after a certain amount of steps

        Parameter dt: The number of seconds since the last animation frame
        Precondition: dt is an number >= 0
        """
        if self._steps > self._boltSpeed:

            #get a list containing the indicies of the nonempty  colomns of aliens
            validColomns = self.validColomns()

            #choose a random colomn from that list
            column = random.choice(validColomns)

            #get the bottom most alien of the colomn
            bottom = self.bottomAlien(column)

            #create an alien bolt at the given bottom alien
            self._bolts.append(Bolt(self._aliens[bottom][column].getX(),
                                    self._aliens[bottom][column].getY() -
                                    ALIEN_HEIGHT, -BOLT_SPEED))
            self._boltSpeed = random.randrange(BOLT_RATE)
            self._steps = 0

    def validColomns(self):
        """
        Returns a list containing the indicies of colomns in self._aliens
        that are not empty
        """
        valid = []

        for row in self._aliens:
            for alien in row:
                if alien != None and row.index(alien) not in valid:
                    valid.append(row.index(alien))

        return valid

    def bottomAlien(self, column):
        """
        Returns the bottom most alien in the given column of self._aliens

        Parameter column: the index of a nonepty column in self._aliens
        Precondition: an int
        """
        bottom = ALIEN_ROWS - 1
        for x in range(ALIEN_ROWS):
            if self._aliens[bottom][column] != None:
                return bottom
            else:
                bottom = bottom -1

    #HELPER METHODS TO ANIMATE THE SHIP
    def _destroyShip(self):
        """
        Helper method that waits for the ship to be hit by an alien bolt, so it can
        start the ship's death animation, subtract a life, and remove the alien
        bolt from self._bolts.
        """

        for bolt in self._bolts:
            if self._ship != None and self._ship.collides(bolt) == True:

                #create animator for ship death animation
                self._animator = self._ship.makeAnimator()
                next(self._animator)

                #remove bolt from list
                self._bolts.remove(bolt)
                self._sounds[self._lives].play()
                self._lives = self._lives -1

    def runShipAnimator(self, dt):
        """
        The driver for the ship's animation coroutine

        Parameter dt: The number of seconds since the last animation frame
        Precondition: dt is an number >= 0
        """
        try:
            self._animator.send(dt)
        except:
            self._animator = None
            self._ship = None
            self._bolts = []

    #HELPER METHODS TO ANIMATE THE ALIENS <-- ADDITIONAL FEATURE
    def _destroyAliens(self):
        """
        Helper method that waits for an alien to be hit by a player bolt, so it can
        start the alien's death animation and remove the player's bot from
        from self._bolts.
        """
        for row in self._aliens:
            for alien in row:
                for bolt in self._bolts:
                    if alien != None and alien.collides(bolt) == True:
                        self._index1 = self._aliens.index(row)
                        self._index2 = row.index(alien)
                        self._alienAnimator = alien.makeAnimator(alien)
                        next(self._alienAnimator)
                        self._sounds[4].play()

                        self._bolts.remove(bolt)

    def runAlienAnimator(self, dt):
        """
        The driver for the alien's animation coroutine

        Parameter dt: The number of seconds since the last animation frame
        Precondition: dt is an number >= 0
        """
        try:
            self._alienAnimator.send(dt)
        except:
            self._aliens[self._index1][self._index2] = None
            self._alienAnimator = None

    def _walkAliens(self):
        """
        Helper method that creates an alien walking animation by switching all the aliens
        between frames 0 and frame 1.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None and alien.frame == 0:
                    alien.setFrame(1)
                elif alien != None and alien.frame == 1:
                    alien.setFrame(0)

    #HELPER METHOD TO BE USED BY APP.PY TO CREATE A SHIP
    def createShip(self):
        """
        Helper method that Creates a ship object and enters it into self._ship
        """
        self._ship = Ship()

    #HELPER METHOD THAT DETERMINES THE GAME OUTCOME
    def _checkOutcome(self):
        """
        Helper method that determines the game outcome and stores it in self._outcome
        """
        allDead = True
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    allDead = False

        belowLine = False
        for row in self._aliens:
            for alien in row:
                    if alien != None and alien.getY() - ALIEN_HEIGHT/2 < DEFENSE_LINE:
                        belowLine = True

        if allDead == True:
            self._outcome = "win"
        elif belowLine == True:
            self._outcome = "lose"
        elif self._lives == 0:
            self._outcome = "lose"

    #HELPER METHOD FOR SOUNDS <-- ADDITIONAL FEATURE
    def _muteSounds(self, input):
        """
        Helper method that turns the key "m" into a mute button. When "m" is pressed
        once all sounds are muted. When it is pressed for a second time, the sounds
        are turned back on.

        Parameter input: the given input.
        Precondition: an instance of GInput.
        """
        currentSound = input.is_key_down('m')

        if currentSound == True and self._lastM == False:
            self._mute = self._mute + 1

        if self._mute % 2 == 0:
            for x in self._sounds:
                x.volume = 1
        elif self._mute%2 == 1:
            for x in self._sounds:
                x.volume = 0

        self._lastM = currentSound
