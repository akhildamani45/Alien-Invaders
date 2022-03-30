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

    All of the attributes of this class ar to be hidden. You may find that
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

    # Attribute _direction: the direction the aliens are marching
    # Invariant: _direction is a boolean such that if the aliens are marching right
    # it is True and if they are marching left it is False
    #
    # Attribute _count: the number of aliens steps before they shoot
    # Invariant: _count is an int
    #
    # Attribute _randomfire: randomly chosen alien shoots
    # Invariant: _randomfire is an int that is randomly chosen between
    #
    # Attribute _animator: A coroutine for performing an animation
    # Invariant: _animator is a generator-based coroutine (or None)
    #
    # Attribute _aliencross: Shows when the aliens have
    # crossed the defensive line
    # Invariant: _aliencross is a boolean that is initially False and
    # only becomes True when an alien has crossed the defensive line
    #
    # Attribute _victory: Shows when all the aliens have been killed
    # Invariant: _victory is a boolean that is False and only becomes True when
    # all the aliens have been killed


    def getaliencross(self):
        """
        returns self._aliencross
        """
        return self._aliencross


    def getvictory(self):
        """
        Returns self._victory
        """
        return self._victory


    def getlives(self):
        """
        Returns self._lives
        """
        return self._lives


    def getship(self):
        """
        return self._ship
        """
        return self._ship


    def __init__(self):
        """
        intilaizes the wave
        """
        self.makealiens()
        self._ship = Ship()
        self._bolts = []
        self._time = 0
        self._direction = True
        self._count = 0
        self._dline = GPath(linewidth = 2,
        points = [0, DEFENSE_LINE, GAME_WIDTH, DEFENSE_LINE],
         linecolor = 'black')
        self._randomfire = random.randint(1, BOLT_RATE)
        self._animator = None
        self._lives = 3
        self._victory = False
        self._aliencross = False


    def update(self, input, dt):
        """
        updates the wave to move ship aliens and bolts
        """
        list = []
        for x in range(len(self._aliens[0])):
            for y in range(len(self._aliens)):
                if self._aliens[y][x] is not None:
                    list.append(self._aliens[y][x].y)
        y = min(list)
        if y < DEFENSE_LINE:
            self._aliencross = True
        self.moveship(input)
        self.movealiens(dt)
        self.makebolts(input, dt)
        self.removealien()
        self.corountine(dt)
        end = True
        for x in range(len(self._aliens)):
            for y in range(len(self._aliens[0])):
                if self._aliens[x][y] is not None:
                    end = False
        self._victory = end


    def draw(self, view):
        """
        draws the wave
        """
        for row in self._aliens:
            for alien in row:
                if alien is not None:
                    alien.draw(view)
        if self._ship is not None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)


    def makealiens(self):
        """
        creates list of alien objects and assigns it to _aliens
        """
        result = []
        if ALIEN_ROWS % 2 == 0:
            count = 0
        else:
            count = 1
        num = 0
        ny = GAME_HEIGHT - (ALIEN_CEILING + ALIEN_HEIGHT/2)
        for r in range(ALIEN_ROWS):
            nx = ALIEN_H_SEP + ALIEN_WIDTH/2
            nlist = []
            if count % 2 == 0 and count != 0:
                num += 1
            if num >= len(ALIEN_IMAGES):
                num = 0
            count += 1
            for c in range(ALIENS_IN_ROW):
                onealien = Alien(x = nx, y = ny, source = ALIEN_IMAGES[num])
                nlist.append(onealien)
                nx += ALIEN_H_SEP + ALIEN_WIDTH
            ny -= (ALIEN_V_SEP + ALIEN_HEIGHT)
            result.append(nlist)
        self._aliens = result


    def moveship(self, input):
        """
        moves ship
        """
        if self._animator is None:
            if self._ship is not None and input.is_key_down('left'):
                self._ship.x -= SHIP_MOVEMENT
                self._ship.x = max(self._ship.x, SHIP_WIDTH/2)
            if self._ship is not None and input.is_key_down('right'):
                self._ship.x += SHIP_MOVEMENT
                self._ship.x = min(self._ship.x, GAME_WIDTH - SHIP_WIDTH/2)


    def movealiens(self, dt):
        """
        moves aliens
        """
        self._time += dt
        right = self.rmost()
        if self._direction:
            if self._time > ALIEN_SPEED:
                for row in self._aliens:
                    for alien in row:
                        if alien is not None:
                            alien.x += ALIEN_H_WALK
                self._time = 0
                self._count += 1
                if GAME_WIDTH - right < ALIEN_H_SEP:
                        for row in self._aliens:
                            for alien in row:
                                if alien is not None:
                                    alien.y -= ALIEN_V_SEP
                                    alien.x -= ALIEN_H_WALK
                        self._direction = not self._direction
        else:
            self.lmove()


    def lmove(self):
        """
        moves left or down
        """
        left = self.lmost()
        if self._time > ALIEN_SPEED:
            for row in self._aliens:
                for alien in row:
                    if alien is not None:
                        alien.x -= ALIEN_H_WALK
            self._time = 0
            self._count += 1
            if left < ALIEN_H_SEP + ALIEN_WIDTH:
                    for row in self._aliens:
                        for alien in row:
                            if alien is not None:
                                alien.y -= ALIEN_V_SEP
                                alien.x += ALIEN_H_WALK
                    self._direction = not self._direction


    def rmost(self):
        """
        returns the position of rightmost alien
        """
        list = []
        for row in self._aliens:
            for alien in row:
                if alien is not None:
                    list.append(alien.x)
        right = max(list) + ALIEN_WIDTH/2
        return right


    def lmost(self):
        """
        returns the position of the left most alien
        """
        list = []
        for row in self._aliens:
            for alien in row:
                if alien is not None:
                    list.append(alien.x)
        left = min(list) + ALIEN_WIDTH/2
        return left


    def makebolts(self, input, dt):
        """
        creates bolts
        """
        if self._animator is None\
        and self._ship is not None and input.is_key_down('up'):
            if not self.restrict():
                self._bolts.append(Bolt(x = self._ship.x,
                y = SHIP_BOTTOM + SHIP_HEIGHT, velocity = BOLT_SPEED))
        if self._randomfire - self._count == 0 :
            self.randalien()
            self._randomfire = random.randint(1, BOLT_RATE)
            self._count = 0
        for x in range(len(self._bolts)):
                self._bolts[x].y += self._bolts[x].getvelocity()
        i = 0
        while i < len(self._bolts):
            if self._bolts[i].bottom > GAME_HEIGHT or self._bolts[i].top < 0:
                del self._bolts[i]
            else:
                i += 1


    def restrict(self):
        """
        if there is a player bolt in self._bolts returns True
        """
        for x in range(len(self._bolts)):
            if self._bolts[x].isplayerbolt():
                return True


    def randalien(self):
        """
        picks alien at random to shoot
        """
        list = []
        r = random.randint(0, len(self._aliens[0])-1)
        for x in range(len(self._aliens[0])):
            for y in range(len(self._aliens)):
                if self._aliens[y][r] is not None:
                    list.append(self._aliens[y][r].y)
                    nx = self._aliens[y][r].x
                else:
                    r = random.randint(0, len(self._aliens[0])-1)
            if list != []:
                y = min(list)
                result = self._bolts.append(Bolt(x = nx,
                y = y - ALIEN_HEIGHT/2, velocity = -BOLT_SPEED))
                return result


    def removeship(self):
        """
        removes ship when shot
        """
        for x in range(len(self._bolts)):
            if self._ship is not None and self._ship.collides(self._bolts[x]):
                self._ship = None
                self._bolts.remove(self._bolts[x])


    def removealien(self):
        """
        removes aliens when shot
        """
        for x in self._bolts:
            for c in range(len(self._aliens[0])):
                for r in range(len(self._aliens)):
                    if self._aliens[r][c] is not None\
                    and self._aliens[r][c].collides(x):
                        self._aliens[r][c] = None
                        self._bolts.remove(x)


    def corountine(self, dt):
        """
        runs the coroutine
        """
        if not self._animator is None:
            try:
                self._animator.send(dt)
            except:
                self._animator = None
                self._bolts.clear()
                self._ship = None
                self._lives -= 1
        elif self._ship is not None and self.r():
            self._animator = self._ship._animate_ship(dt)
            next(self._animator)


    def r(self):
        """
        Returns true if ship collides with an alien bolt
        """
        for x in range(len(self._bolts)):
            if self._ship is not None and self._ship.collides(self._bolts[x]):
                return True
