# Cluster spot-check (k=100, BAAI/bge-base-en-v1.5, 59702 unique math prompts)

Each cluster: size, top terms, the 3 prompts nearest its centroid. Look for clusters that are formatting artefacts (e.g. 'answer in the form') instead of topics.

| min | median | max |
|---|---|---|
| 181 | 568 | 1242 |

## cluster 56 -- 1242 prompts -- mathbb, functions, rightarrow, real, functional, satisfy, equation, numbers
- Find all functions \( f: \mathbb{R} \to \mathbb{R} \) such that \[ f(x + f(y)) + f(2 + f(y) - x) = y(x - 1)f(y) \] for all \( x, y \in \mathbb{R} \).
- Find all functions \( f: \mathbb{R} \to \mathbb{R} \) such that \( f(x+y)f(x-y) + 1 = (f(x) + f(y))(x + y) + 2f(x) - y \) for all \( x, y \in \mathbb{R} \).
- Find all functions \( f : \mathbb{R} \to \mathbb{R} \) such that \[ f(x - f(y)) = 2f(x) + x + f(y) \] for all \( x, y \in \mathbb{R} \).

## cluster 59 -- 1167 prompts -- probability, randomly, random, balls, chosen, dice, number, heads
- Forty slips are placed into a hat, each bearing a number from 1 to 10, with each number entered on four slips. Four slips are drawn from the hat at random and without replacement. Let \( p \) be the probability that all 
- Let \( n \geq 3 \) be an integer. Throw a dice \( n \) times, and let \( X_1, X_2, \cdots, X_n \) be the outcomes in this order. For \( i = 2, 3, \cdots, n \), denote \( A_i \) as the event that \( X_i = X_{i-1} \). What
- Each of the 20 balls is tossed independently and at random into one of the 5 bins. Let \( p \) be the probability that some bin ends up with 3 balls, another with 5 balls, and the other three with 4 balls each. Let \( q 

## cluster 15 -- 1157 prompts -- triangle, abc, let, respectively, point, circumcircle, points, intersects
- Let \(ABC\) be an acute triangle with circumcenter \(O\), and the perpendicular bisector of \(BC\) intersects \(AB\) and \(AC\) at \(E\) and \(F\), respectively. Let \(H\) and \(K\) be the orthocenters of \(\triangle ABC
- Let \(ABC\) be an acute triangle with circumcenter \(O\) and circumcircle \(\Omega\). Choose points \(D, E\) from sides \(AB, AC\), respectively, and let \(\ell\) be the line passing through \(A\) and perpendicular to \(
- In triangle \(ABC\) with incenter \(I\) and \(A\)-excenter \(I_a\), let \(\omega\) be the circumcircle of \(\triangle ABC\) and \(D\) be the intersection of \(AI\) and \(\omega\). A line \(r\) through \(D\) intersects \(

## cluster 88 -- 1155 prompts -- smallest, positive, integer, integers, value, frac, let, possible
- For a positive integer \( n \), let \( S_n \) be the set of all positive integers \( a_1 < a_2 < \cdots < a_n \) such that \( a_i - a_j \) divides \( a_i \) for all \( i < j + 1 \). Find the smallest possible value of \(
- Find the smallest positive integer \(N\) such that there exist integers \(a\), \(b\), and \(c\) with \(|a|, |b|, |c| < N\) and \(|a + b\sqrt{2} + c\sqrt{3}| < 10^{-11}\).
- Let \( m, n \geq 2 \) be positive integers and \( a_1, a_2, \ldots, a_n \) be integers none of which are divisible by \( m^{n-1} \). Find the smallest positive integer \( k \) such that there exist integers \( e_1, e_2, 

## cluster 24 -- 1123 prompts -- maximum, value, frac, expression, sqrt, real, numbers, let
- Given \(a, b, c > 0\) and \(a + b + abc = c\), find the maximum value of  \[ A = \frac{2}{1+a^2} + \frac{3}{1+c^2} - \frac{2}{1+b^2}. \]
- Let \(a, b, c > 0\) be such that \(a + b + c = 3\). Find the maximum value of  \[ A = \frac{1}{4a^2 + b^2 + c^2} + \frac{1}{4b^2 + a^2 + c^2} + \frac{1}{4c^2 + b^2 + a^2}. \]
- Find the maximum value of  \[ \frac{a^{2}b^{2}c^{2}}{(a^2+ab+b^2)(b^2+bc+c^2)(c^2+ca+a^2)} \] when \(a + b + c = 0\) and \(a, b, c\) are real numbers.

## cluster 10 -- 981 prompts -- point, line, points, parabola, equation, curve, frac, axis
- Let \(a, b\) be positive numbers. In the \(xy\)-plane, let \(C\) be the part of the ellipse \(E: ax^2 + by^2 = 1\) with \(x \geq 0\) and \(y \leq 0\). Let \(l_t\) be the half-line \(y = tx\) with \(x \geq 0\) and slope \
- Let \( B \) and \( C \) be two fixed points, \( l \) be a fixed line parallel to \( BC \), and \( \omega \) be a fixed circle passing through \( B \) and \( C \). Let \( P \) be a variable point on \( l \) and \( N_P \) 
- Given two points \( P \) and \( Q \) on the parabola \( y = x^2 \), let \( h \) be the \( y \)-coordinate of the midpoint of the segment \( PQ \). Let \( L \) and \( m \) be the length and slope of the segment \( PQ \) r

## cluster 76 -- 974 prompts -- angle, triangle, abc, circ, point, frac, let, sin
- Let \(ABC\) be a triangle with point \(D\) on segment \([AC]\). Given that \(|AB| = x\), \(|BD| = y\), \(|AC| = x + y\), \(\angle ABD = 18^\circ\), and \(\angle CBD = 9^\circ\), find \(\angle ACB\). Both synthetic and an
- In the triangle \( ABC \), \(\angle B = 90^\circ\), \(\angle C = 20^\circ\), \( D \) and \( E \) are points on \( BC \) such that \(\angle ADC =140^\circ\) and \(\angle AEC =150^\circ\). Suppose \( AD=10 \). Find \( BD \
- In \( \triangle ABC \), \( \angle ABC = 45^\circ \). Point \( D \) is on \( \overline{BC} \) such that \( 2 \cdot BD = CD \) and \( \angle DAB = 15^\circ \). Find \( \angle ACB \).

## cluster 75 -- 967 prompts -- set, elements, subsets, ldots, subset, number, element, sets
- Consider the set \( S = \{1, 2, \cdots, 2^n\} \). Let \( A \) be a subset of \( S \) with \( n \) elements such that for any two different non-empty subsets of \( A \), the sum of the elements of one subset does not divi
- Given a set \( A \) of \( n \) elements and positive integers \( k \) and \( m \) such that \( 4 \leq k < n \) and \( m \leq \min \{k-3, \frac{n}{2}\} \). Let \( A_1, A_2, \ldots, A_l \) be subsets of \( A \), each with 
- Given the set \( X = \{1, 2, 3, \ldots, 19\} \), we select \( k \) arbitrary 7-element subsets of \( X \). Let \( A \) be the set of all 8-element subsets \( M \) of \( X \) such that there exists a 7-element subset (amo

## cluster 60 -- 958 prompts -- triangle, point, points, abc, line, respectively, prove, let
- On the sides \( AB, BC \), and \( AC \) of the triangle \( ABC \), points \( P, M \), and \( K \) are taken such that the segments \( AM, BK \), and \( CP \) intersect at one point and \(\overrightarrow{AM} + \overrighta
- In triangle \(ABC\) with \(AB < AC\) and \(AB + AC = 2BC\), let \(M\) be the midpoint of \(\overline{BC}\). Choose point \(P\) on the extension of \(\overline{BA}\) past \(A\) and point \(Q\) on segment \(\overline{AC}\)
- On the sides $BC$, $CA$, and $AB$ of triangle $ABC$, points $A_{1}$, $B_{1}$, and $C_{1}$ are taken such that segments $AA_{1}$, $BB_{1}$, and $CC_{1}$ intersect at one point. Lines $A_{1}B_{1}$ and $A_{1}C_{1}$ intersec

## cluster 87 -- 926 prompts -- times, grid, squares, square, cells, number, cube, cell
- For some positive integer $n$, consider an $n \times n$ board. On this board, you can place any number of rectangles with sides along the grid lines. What is the smallest number of such rectangles that must be placed so 
- Let \( k \) and \( n \) be integers such that \( 2 \leq k \leq n \leq 2k - 1 \). Consider an \( n \times n \) grid. Rectangles \( 1 \times k \) or \( k \times 1 \) are added to the grid, each covering exactly \( k \) squ
- Consider a $10 \times 10$ board that is to be tiled using 25 pieces of type $A$. Each piece of type $A$ covers exactly 4 squares. Determine the number of distinct ways to color the board using two colors such that no pie

## cluster 68 -- 921 prompts -- circle, point, points, tangent, line, circles, omega, intersects
- Let \(PA\) and \(PB\) be tangents to a circle \(\omega\) at points \(A\) and \(B\). Let \(M\) be a point on \(AP\), and \(N\) be the midpoint of \(AB\). Line \(MN\) intersects the circle at point \(C\) (with \(N\) betwee
- From a point \( P \) outside a circle, two tangents and one secant are drawn to the circle. The tangents touch the circle at points \( A \) and \( B \), and the secant intersects the circle at points \( C \) and \( D \),
- Consider two circles \( C1 \) and \( C2 \) that touch externally at point \( M \), with \( C2 \) having a larger radius than \( C1 \). Let \( A \) be a point on \( C2 \) not lying on the line connecting the centers of th

## cluster 8 -- 919 prompts -- day, number, candies, days, total, did, age, year
- Petya says to his neighbor Vova: "There are 30 people in our class and an interesting situation is observed: any two boys have different numbers of girlfriends in the class, and any two girls have different numbers of bo
- There are 28 sweets on a table. Peter finds some of them delicious. In one move, Alex can indicate any set of sweets and ask Peter how many of them are delicious. How can Alex find all the delicious sweets in 21 moves?
- Greedy Vovochka has 25 classmates. For his birthday, he brought 200 candies to class. Vovochka's mother, so that he does not eat everything himself, ordered him to distribute the candies in such a way that any 16 of his 

## cluster 22 -- 909 prompts -- function, frac, mathbb, given, left, right, let, value
- It is given that \( f(x) = \frac{1}{3} x^{3} - 2 x^{2} + \frac{2}{3} x^{3} + 3 x^{2} + 5 x + 7 - 4 x \). If \( f(-2) = b \), find \( b \).
- Find the function \( f(x) \) that satisfies the following conditions: - \( f(x): \mathbb{N}^* \rightarrow \mathbb{N}^* \) - \( f(1) = a \) - \( f(x+1)f(x) = f(x)^2 + 2f(x) - 1 \)
- For \( x \in \mathbb{R} \), the function \( f \) satisfies \( f(x) = f(x + 2) - 3 \) and \( f(x + 1) = x \). Given that \( f(3) = 2 \), find \( f(5) \).

## cluster 13 -- 901 prompts -- integers, positive, integer, sum, divisible, number, divisors, ldots
- For positive integers \( n \), let \( \tau(n) \) denote the number of positive integer divisors of \( n \). Define \( S(n) \) by  \[ S(n) = \tau(1) + \tau(2) + \cdots + \tau(n). \] Let \( a \) denote the number of positi
- Given a positive integer \( n \), how many ways can \( n \) be written as a sum of one or more positive integers \( a_1 \leq a_2 \leq \ldots \leq a_k \) such that \( a_k - a_1 = 0 \) or \( 1 \)?
- Given a positive integer \( n > 1 \), determine if there exist \( 2n \) pairwise different positive integers \( a_1, \ldots, a_n, b_1, \ldots, b_n \) such that \( a_1 + \ldots + a_n = b_1 + \ldots + b_n \) and \[ n-1 > \

## cluster 44 -- 867 prompts -- circle, radius, circles, inscribed, area, tangent, triangle, length
- In the diagram, circles \( C_1, C_2, C_3, \) and \( L \) are all tangent to each other. \( C_1 \) and \( C_2 \) have radii of 5, and \( C_3 \) has a radius of 8. The problem is to find the radius of circle \( L \).
- The diagram shows a circle with centre \( O \) and a triangle \( O P Q \). Side \( P Q \) is a tangent to the circle. The area of the circle is equal to the area of the triangle.  What is the ratio of the length of \( P 
- Circles \( C \) and \( D \) intersect at points \( A \) and \( B \). The diameter \( CA \) of circle \( C \) is tangent to circle \( D \) at \( A \), and point \( D \) is such that \( C \), \( B \), and \( D \) are colli

## cluster 16 -- 857 prompts -- numbers, number, sum, written, board, digit, row, integers
- Let \( n \) be an integer such that \( 10^{98} \le n < 10^{100} \). Numbers \( 1, 2, \ldots, n \) are written on a board. An operation is performed where the \( m^2 \)-th smallest number is erased for each positive integ
- On the board, there are $n>3$ different natural numbers, each less than $(n-1)!$. For each pair of these numbers, Seryozha divided the larger by the smaller, recording the quotient in his notebook. (For example, if he di
- For an integer \( n > 1 \), the numbers \( 1, 2, 3, \ldots, n \) are written in order on a blackboard. The following moves are possible:  (i) Take three adjacent numbers \( x, y, z \) whose sum is a multiple of 3 and rep

## cluster 61 -- 829 prompts -- points, plane, point, lines, line, number, set, distance
- In a plane, there are \( n \) red points and \( n \) blue points, with no three points lying on a single straight line. Prove that it is possible to draw \( n \) line segments with endpoints of different colors such that
- Let \( n \) be an integer greater than 2, and \( P_1, P_2, \cdots, P_n \) be distinct points in the plane. Let \( \mathcal{S} \) denote the union of all segments \( P_1P_2, P_2P_3, \dots, P_{n-1}P_n \). Determine if it i
- Let \( n \) be an integer greater than 2, and \( P_1, P_2, \cdots, P_n \) be distinct points in the plane. Let \( \mathcal{S} \) denote the union of all segments \( P_1P_2, P_2P_3, \dots, P_{n-1}P_n \). Determine if it i

## cluster 84 -- 826 prompts -- sum, frac, series, infty, binom, cdots, cdot, value
- Find the sum of the series \(1 + \frac{1+2}{2!} + \frac{1+2+2^2}{3!} + \cdots\) up to the \(n\)th term.
- Find the value of the sum: \[ \sum_{n=0}^{\infty} \frac{(-1)^n (n+1)}{(n+2) n! 2^{n-1}} \]
- Find the sum of the series up to \( n \) terms: \[ \sum_{k=1}^{n} \frac{1}{k(k+1)} \]

## cluster 70 -- 823 prompts -- triangle, triangles, sides, lengths, equilateral, perimeter, length, area
- On the sides of triangle \(ABC\), three similar isosceles triangles \(ABP\) (\(AP = PB\)), \(AQC\) (\(AQ = QC\)), and \(BRC\) (\(BR = RC\)) are constructed. The first two are constructed externally to the triangle \(ABC\
- In a right triangle \( \triangle ABC \), the lengths of the hypotenuse \( AB \) and the leg \( AC \) satisfy the inequalities \( 100 < AB < 101 \) and \( 99 < AC < 100 \). Prove that \(\triangle ABC\) can be divided into
- Given a triangle \(ABC\) and a point \(P\) inside it, denote by \(d_a\), \(d_b\), and \(d_c\) the distances from \(P\) to the sides \(BC\), \(CA\), and \(AB\) respectively. Let \(a\), \(b\), and \(c\) be the lengths of t

## cluster 35 -- 788 prompts -- people, students, ways, number, group, person, girls, boys
- In a class of 31 people, each group of 4 students contains at least one student who is friends with the other 3 students. What is the minimum number of students who are friends with all the other students except themselv
- In a party, each person knows exactly 25 other people. It is given that: (a) For every pair of people $A$ and $B$ who know each other, nobody else knows both $A$ and $B$. (b) For every pair of people $A$ and $B$ who do n
- In a group of $n \ge 5$ people, where every two people who do not know each other have exactly one mutual friend and no one knows everyone else, determine the number of ways to select and seat 5 of these people around a 

## cluster 30 -- 786 prompts -- triangle, area, abc, point, abcd, angle, sides, respectively
- Triangle \(ABC\) has side lengths \(AB=2\sqrt{5}\), \(BC=1\), and \(CA=5\). Point \(D\) is on side \(AC\) such that \(CD=1\), and \(F\) is a point such that \(BF=2\) and \(CF=3\). Let \(E\) be the intersection of lines \
- Let \(ABC\) be a triangle with \(AB=5\), \(BC=6\), and \(AC=7\). Let \(M\) be the midpoint of \(BC\) and \(N\) the midpoint of \(AC\). If \(AM\) intersects the circumcircle of \(ABC\) at \(P\) and \(BN\) intersects it at
- In triangle \( ABC \), point \( D \) is the midpoint of \( BC \) and point \( E \) is the midpoint of \( AC \). If \( AD = 6 \), \( BE = 9 \), and \( AC = 10 \), find the area of triangle \( ABC \).

## cluster 29 -- 771 prompts -- digit, digits, numbers, number, divisible, formed, sum, integers
- How many numbers can be formed using the digits $0, 1, 2, 3, 4, 5, 6, 7, 8, 9$ without repetition that are divisible by $7$?
- For a given positive integer \( n \), how many \( n \)-digit natural numbers can be formed from the digits 1, 2, 3, 4, and 5 such that an odd number of 1's and an even number of 2's are used?
- How many 6-digit numbers are there such that the digits of each number are all from the set $\{1,2,3,4,5\}$ and any digit that appears in the number appears at least twice?

## cluster 97 -- 760 prompts -- quadrilateral, abcd, angle, convex, let, point, diagonals, respectively
- Let \(ABCD\) be a convex quadrilateral with \(\angle BAC = 50^\circ\), \(\angle CAD = 60^\circ\), \(\angle CBD = 30^\circ\), and \(\angle BDC = 25^\circ\). If \(E\) is the point of intersection of \(AC\) and \(BD\), find
- For a convex quadrilateral \(ABCD\), let \(AC\) and \(BD\) intersect at \(P\). Let \(M\) be the midpoint of \(AD\), and \(MP\) meet \(BC\) at \(E\). Given that \(\frac{BE}{EC} = \frac{AB^2}{CD^2}\), \(\angle A = 63^\circ
- Given quadrilateral \(ABCD\) inscribed in circle \((O)\). Let \(AD\) intersect \(BC\) at \(E\) and \(AB\) intersect \(CD\) at \(F\). Let \(M\), \(N\), and \(P\) be the midpoints of \(AC\), \(BD\), and \(EF\) respectively

## cluster 89 -- 742 prompts -- prime, number, let, numbers, integer, positive, sum, integers
- Determine if there exist integers \(n, a_1, a_2, \ldots, a_{2012}\) such that  \[ n^2 = \sum_{1 \leq i \leq 2012} a_i^{p_i} \]  where \(p_i\) is the \(i\)-th prime number (\(p_1 = 2, p_2 = 3, p_3 = 5, p_4 = 7, \ldots\)) 
- For a given positive integer \( k \), let \( p_k \) be the smallest prime number such that there exist distinct integers \( a_1, a_2, \ldots, a_{k+3} \in \{1, 2, \ldots, p_k-1\} \) satisfying \( p_k \) divides \( a_i a_{
- Let \( p > 2 \) be a prime number, \( k \in \mathbb{Z}^+ \) and \( k < p \). Let \( n = kp^2 + 1 \). Suppose \( 2^{n-1} \equiv 1 \pmod{n} \) and \( 2^k \not\equiv 1 \pmod{n} \). Find the smallest possible value of \( n \

## cluster 34 -- 740 prompts -- time, speed, minutes, hour, hours, distance, meters, minute
- A and B start traveling towards each other from points A and B simultaneously. A travels at 60 meters per minute and B travels at 40 meters per minute. After some time, they meet at a point 300 meters from the midpoint b
- Alex drives from point \( P \) to point \( Q \), then immediately returns to \( P \). Bob drives from point \( Q \) to point \( P \), then immediately returns to \( Q \). They travel on the same road, start at the same t
- From point \(A\) to point \(B\), the distance between which is 10 km, a car left at 7:00 AM. After traveling \(\frac{2}{3}\) of the way, the car passed point \(C\), from which a cyclist departed at that moment towards po

## cluster 32 -- 734 prompts -- frac, sqrt, value, times, cdot, fraction, pmod, compute
- The value of \( 8 - \frac{6}{4 - 2} \) is (A) 5 (B) 1 (C) \( \frac{7}{2} \) (D) \( \frac{17}{2} \) (E) 7
- If \( w = 4 \), \( x = 9 \), and \( z = 25 \), then \( \sqrt{\frac{w}{x}} + \sqrt{\frac{x}{z}} \) equals (A) \( \frac{5}{8} \) (B) \( \frac{19}{15} \) (C) \( \frac{77}{225} \) (D) \( \frac{181}{225} \) (E) \( \frac{2}{5}
- Find the numbers \( n \in \mathbb{N}^* \) and \( r_1 < r_2 < r_3 < \ldots < r_n \in \mathbb{N}^* \) such that:  \[ \frac{17}{18} = \frac{1}{r_1} + \frac{1}{r_2} + \ldots + \frac{1}{r_n}. \]

## cluster 31 -- 729 prompts -- polynomial, coefficients, degree, integer, polynomials, let, mathbb, ldots
- Find all positive integers \( n \) such that if \( p(x) \) is a polynomial with integer coefficients and \( 0 \leq p(k) \leq n \) for \( k = 0, 1, 2, \ldots, n+1 \), then \( p(0) = p(1) = \ldots = p(n+1) \).
- For any real number \( x \) and positive integers \( m \) and \( n \), let \( P(x) \) be the number of distinct polynomials \( f \) in two variables with integer coefficients such that there exists a polynomial \( g \) w
- Determine the polynomial \( P \in \mathbb{R}[x] \) for which there exists \( n \in \mathbb{Z}_{>0} \) such that for all \( x \in \mathbb{Q} \), the following holds: \[ P\left(x+\frac{1}{n}\right) + P\left(x-\frac{1}{n}\r

## cluster 41 -- 714 prompts -- player, game, players, wins, play, strategy, winning, number
- Two players play alternately. The first player is given a pair of positive integers \((x_1, y_1)\). Each player must replace the pair \((x_n, y_n)\) that he is given by a pair of non-negative integers \((x_{n+1}, y_{n+1}
- Initially, there is a supply of \(2n+1\) chips. Players A and B take turns to remove any number of chips from 1 to \(k\). The game ends when one player has an even number of chips and the other has an odd number. The pla
- Two players, \( A \) and \( B \), play a game on a circle with 10 cells. Player \( A \) starts, and they take turns choosing a free cell and writing either \( O \) or \( M \) in it. The player who first creates the seque

## cluster 54 -- 688 prompts -- inequality, frac, holds, sqrt, geq, real, solve, leq
- Find \( k \in \mathbb{R} \) such that for all \( a, b, c \geq 0 \), the inequality \( \sqrt{3a^2 + 3b^2 + 3c^2} \leq a + b + c + k \sqrt{a^2 + b^2 + c^2 - ab - bc - ac} \) holds.
- Find the best constant \( c \) such that for any positive real numbers \( a_1, a_2, \ldots, a_n \) and any \( n \geq 3 \), the following inequality holds: \[ \frac{a_1}{a_2 + a_3} + \frac{a_2}{a_3 + a_4} + \cdots + \frac
- Find \(\alpha, k > 0\) for which the inequality \[ \sqrt{1 + \alpha \sum{(a-b)^2}} + k \cdot \sqrt[3]{abcd} \geq \frac{(k+1)(a+b+c+d)}{4} \] holds for all \(a, b, c, d \geq 0\), where \(\sum{(a-b)^2} = (a-b)^2 + (a-c)^2 

## cluster 53 -- 680 prompts -- mathbb, functions, rightarrow, function, integers, positive, satisfy, let
- Find all functions \( f: \mathbb{N} \rightarrow \mathbb{N} \) such that \( f(m+n)f(m-n) = f(m^2) \) holds for all integers \( m \) and \( n \) with \( m > n > 0 \).
- Find all functions \( f: \mathbb{N} \to \mathbb{N} \) and \( g: \mathbb{N} \to \mathbb{N} \) such that for any two positive integers \( m, n \), \[ f(m) - f(n) = (m - n)(g(m) - g(n)). \]
- Find all functions \( f: \mathbb{N} \to \mathbb{N} \) such that \( f(f(n) - n) = f(n) + 1 \) for all \( n \in \mathbb{N} \).

## cluster 72 -- 680 prompts -- minimum, frac, value, let, sqrt, numbers, real, given
- Let \( a, b, c \in \mathbb{R} \) such that \( abc = 1 \). Find the minimum value of  \[ \frac{a}{(a^2 - bc)^2} + \frac{b}{(b^2 - ca)^2} + \frac{c}{(c^2 - ab)^2}. \]
- Let \( a, b, c \in \mathbb{R}^+ \) where \( a^2 + b^2 + c^2 = 1 \). Find the minimum value of  \[ a + b + c + \frac{3}{ab + bc + ca}. \]
- Let \(a, b, c > 0\) such that \(a + b + c = 3\). Find the minimum value of \((ab + bc + ca) \left(\frac{1}{(3a + 2b - c)^2} + \frac{1}{(3b + 2c - a)^2} + \frac{1}{(3c + 2a - b)^2}\right)\).

## cluster 3 -- 678 prompts -- triangle, ratio, abc, let, point, respectively, intersects, points
- Let \(ABC\) be a triangle with point \(D\) on its sideline \(BC\) such that \(\angle CAD = \angle CBA\). A circle \((O)\) passing through \(B\) and \(D\) intersects \(AB\) and \(AD\) at points \(E\) and \(F\), respective
- Let \(ABC\) be a triangle with \(\angle BAC \ne 90^\circ\). Let \((O)\) and \((I)\) be the circumcircles of triangles \(ABC\) and \(OBC\), respectively. \(AC\) intersects \((I)\) at \(G\) (\(G \ne C\)). \(D\) is an arbit
- Let \(ABC\) be a triangle with \(L\), \(M\), and \(N\) as the midpoints of \(BC\), \(CA\), and \(AB\), respectively. The tangent to the circumcircle of \(ABC\) at \(A\) intersects \(LM\) and \(LN\) at \(P\) and \(Q\), re

## cluster 2 -- 666 prompts -- area, square, rectangle, length, sides, perimeter, rectangles, squares
- The diagram shows a rectangle \(ABCD\) in which \(AB = 1\) metre and \(AD = 4\) metres. The points \(E\) and \(G\) are the midpoints of \(AD\) and \(AB\) respectively, and the points \(F\) and \(H\) are the midpoints of 
- The following rectangle is formed by nine pieces of squares of different sizes. Suppose that each side of square \( E \) is of length \( 7 \) cm. Let the area of the rectangle be \( x \) cm\(^2\). Find the value of \( x 
- The shape in the diagram is made up of a rectangle, a square, and an equilateral triangle, all of which have the same perimeter. The length of the side of the square is \( 9 \mathrm{~cm} \). What is the length of the sho

## cluster 39 -- 665 prompts -- solve, equation, sqrt, frac, mathbb, real, left, right
- Solve the equation \((3 + 2\sqrt{2})^x = (\sqrt{2} - 1)^x + 1\).
- Solve the equation $\sqrt{x^{2}+x}=\sqrt{x+3}-\sqrt{1+\frac{1}{x^{2}}}$.
- Solve the equation \( \sqrt{2x^{2}+x+6} + \sqrt{x^{2}+x+2} = x + \frac{1}{x} \).

## cluster 4 -- 661 prompts -- mathbb, set, function, let, space, infty, subset, define
- Let \( a \in \mathbb{R} \), \( a > 0 \), and \( f: \mathbb{R}^{n} \to \mathbb{R} \) be defined as \( f(x) = |x|^{-a} \) for \( x \in \mathbb{R}^{n} \setminus \{0\} \). Find those \( p \) that satisfy \( 1 \leq p \leq \in
- Let \( A = \{x \mid 0 \leqslant x \leqslant 1\} \), and \( f \) be a mapping from \( A \) to the set of real numbers \( \mathbf{R} \), satisfying: (1) \( f(1) = 1 \); (2) \( f(x) \geqslant 0 \) for all \( x \in A \); (3)
- Work in \( \mathbb{R}^+ \). Suppose \( E \) and \( E^C \) are both unbounded subsets of \( \mathbb{R}^+ \). Let \( x, y \in E \) with \( 1 < x < y \). Define \( g(x, y) \) as the smallest value of \( y' \) such that ther

## cluster 18 -- 633 prompts -- polygon, vertices, convex, regular, gon, diagonals, sides, triangles
- Consider a convex polygon \( P \) with \( n \) sides. \( n-3 \) non-intersecting diagonals are drawn so that the polygon is divided into exactly \( n-2 \) triangles. Let \( f(v) \) be the number of triangles having a ver
- Given $n$ points on a plane, forming the vertices of a convex $n$-gon, where $n > 3$. It is known that there exists exactly $k$ equilateral triangles with side length 1, whose vertices are these given points.  a) Prove t
- Given a convex $n$-gon ($n < 10$), we cut the polygon into two pieces by a line that does not pass through any vertices. Repeating this process, we eventually end up with a total of 20 quadrilaterals and 2 pentagons, wit

## cluster 36 -- 629 prompts -- length, triangle, abc, angle, point, segment, let, respectively
- Let \(ABC\) be a triangle with \( \angle ACB = 90^\circ + \frac{1}{2} \angle ABC \). The point \(M\) is the midpoint of the side \(BC\). A circle with center at vertex \(A\) intersects the line \(BC\) at points \(M\) and
- In $\triangle{ABC}$, $\angle{A}=90^\circ$, $AB=AC$. Point $D$ is on $BC$ such that $BD=\frac{BC}{3}$. Line segment $AD$ is drawn, and point $E$ is on $AC$ such that $AD$ and $BE$ are perpendicular to each other. If $AE=8
- In triangle \( ABC \), \( AB = 10 \) and \( AC = 18 \). \( M \) is the midpoint of \( BC \), and the line through \( M \) parallel to the bisector of \( \angle CAB \) cuts \( AC \) at \( D \). Find the length of \( AD \)

## cluster 93 -- 626 prompts -- coins, weights, price, weight, cost, total, rubles, money
- A store sells three types of products, A, B, and C, with prices of 2 yuan, 3 yuan, and 5 yuan per item, respectively. A person bought some quantity of these three products, paying a total of 20 yuan. They discovered that
- Two individuals, A and B, each use the same amount of money to buy the same type of candy. A buys candy in metal boxes, while B buys candy in paper boxes. Both try to buy as many boxes as possible. As a result, A buys 4 
- Helen takes \$50 to buy four books, W, X, Y, Z, where the price of each book is a multiple of 10 cents. After payment, she knows that book W costs half of the payment, while books X and Y cost \(\frac{3}{10}\) and \(\fra

## cluster 17 -- 625 prompts -- roots, equation, real, root, quadratic, frac, values, value
- Let \(a\), \(b\), and \(c\) be the three roots of the equation \(x^3 - (k+1)x^2 + kx + 12 = 0\), where \(k\) is a real number. If \((a-2)^3 + (b-2)^3 + (c-2)^3 = -18\), find the value of \(k\).
- Let \(\alpha\) and \(\beta\) be the roots of \(x^{2}-4x+c=0\), where \(c\) is a real number. If \(-\alpha\) is a root of \(x^{2}+4x-c=0\), find the value of \(\alpha\beta\).
- Find the values of \( a \) such that the equation \( x^4 + ax^3 + bx^2 + ax + 1 = 0 \) has 3 different real roots.

## cluster 63 -- 622 prompts -- matrix, pmatrix, matrices, mathbb, begin, end, times, det
- Let \( D_n = \det(A_n) \), where \[ A_n = \begin{bmatrix} 2 & -1 & 0 & 0 & \cdots & 0 & 0 \\ -1 & 2 & -1 & 0 & \cdots & 0 & 0 \\ 0 & -1 & 2 & -1 & \cdots & 0 & 0 \\ \vdots & \vdots & \vdots & \vdots & \ddots & \vdots & \
- Find a matrix \( X \in M_2(\mathbb{C}) \) such that there exist matrices \( P, Q \in M_2(\mathbb{C}) \) satisfying \( PQ = QP = X \), with \( \det(X) = 0 \) and \( \text{tr}(X) = 1 \).
- Let \( A \in \mathcal{M}_n(\mathbb{C}) \) satisfy \( \det(A + YX) = \det(A + XY) \) for all \( X, Y \in \mathcal{M}_n(\mathbb{C}) \). If \( A \) is a \( 2 \times 2 \) matrix, find the sum of all possible values of \( \de

## cluster 23 -- 620 prompts -- sequence, defined, frac, given, recurrence, term, terms, geq
- The sequence \(a_{1}, a_{2}, \ldots, a_{n}\) is defined by \(a_{1} = 1\) and \(a_{n+1} = 1 + \frac{1}{a_{n}}\) for \(n \geq 1\). Find \(a_{n}\) in terms of \(n\).
- The sequence $\{a_n\}$ is defined by $a_0 = 1$, $a_1 = 1$, and $a_n = a_{n-1} + \frac{a_{n-1}^2}{a_{n-2}}$ for $n \geq 2$. The sequence $\{b_n\}$ is defined by $b_0 = 1$, $b_1 = 3$, and $b_n = b_{n-1} + \frac{b_{n-1}^2}{
- For the sequence \(\{a_n\}\) defined by \(a_1 = 1\), \(a_2 = 2\), \(a_3 = 6\), \(a_4 = 42\), and the recurrence relation \(a_{n+1} = (a_n + 1)a_n\), find the general term \(a_n\).

## cluster 81 -- 614 prompts -- angle, bisector, triangle, abc, bisectors, point, intersects, let
- A triangle \( ABC \) is given. It is known that \( AB=4 \), \( AC=2 \), and \( BC=3 \). The angle bisector of \( \angle BAC \) intersects side \( BC \) at point \( K \). A line passing through point \( B \) parallel to \
- Let \(ABC\) be a triangle with points \(D\) and \(E\) on sides \(BC\) and \(CA\) respectively, such that \(BD = AE\). Segments \(AD\) and \(BE\) intersect at \(P\). The angle bisector of \(\angle BCA\) intersects segment
- Let \(ABC\) be a triangle with points \(D\) and \(E\) on sides \(BC\) and \(CA\) respectively such that \(BD = AE\). Segments \(AD\) and \(BE\) intersect at \(P\). The angle bisector of \(\angle BCA\) intersects segments

## cluster 20 -- 605 prompts -- sequence, positive, ldots, integer, integers, geq, sequences, cdots
- Let \( n > 1 \) be an integer. Find all sequences \( a_1, a_2, \ldots, a_{n^2 + n} \) satisfying the following conditions: (a) \( a_i \in \{0, 1\} \) for all \( 1 \leq i \leq n^2 + n \); (b) \( a_{i+1} + a_{i+2} + \ldots
- Consider a non-zero sequence \(a_{1}, a_{2}, \cdots\) that satisfies: \(a_{1}, a_{2}, \frac{a_{1}^{2} + a_{2}^{2} + b}{a_{1} a_{2}}\) are all integers, and \[a_{n+2} = \frac{a_{n+1}^{2} + b}{a_{n}}, \, n = 1, 2, \cdots,\
- Find the number of sequences consisting of \( n \) positive integers \((a_1, a_2, \ldots, a_n)\) such that \( a_i \geq a_{i-1} \geq 1 \) for \( i = 2, 3, \ldots, n \) and \( a_i \leq i \).

## cluster 9 -- 599 prompts -- sequence, infty, frac, series, sum, lim, convergence, limit
- Let \((x_n)_{n \geq 1}\) be a sequence defined by \(x_{n+1} = x_{n} + \frac{\sqrt{n}}{x_{n}}\). Study the convergence of the sequence \(\frac{x_n}{n^{\frac{3}{4}}}\).
- Consider a sequence of complex numbers \((z_n)_{n \geq 1}\) such that the series \((|z_{n+1}/z_n|)_{n \geq 1}\) and \((|z_{n-1}/z_n|)_{n \geq 1}\) converge. Let \(L\) be the limit of the sequence \((|z_n|)_{n \geq 1}\) a
- Given the sequence \( x_n \) defined by \( x_1 = 1 \) and \( x_{n+1} = x_n^2 + 3x_n + 1 \), let \( u_n = \sum_{k=1}^{n} \frac{1}{x_k + 2} \). Find \( \lim_{n \to \infty} u_n \).

## cluster 38 -- 596 prompts -- lim, infty, limit, frac, left, right, sqrt, evaluate
- Evaluate the limit \[\lim_{n\to \infty}\left(\frac{2n^2-3}{2n^2-n+1}\right)^{\frac{n^2-1}{n}}.\]
- Evaluate the limit \[\lim_{n\to \infty}2^n\left(\sum_{k=1}^n\frac{1}{k(k+2)}-\frac{1}{4}\right)^n\]
- Evaluate the limit \(\lim_{n \to \infty} \left(1 + \frac{1}{2} + \frac{1}{3} + \cdots + \frac{1}{n} - \ln(n)\right)\).

## cluster 45 -- 591 prompts -- sin, cos, frac, tan, circ, alpha, theta, left
- Find the value of \(2(\sin2^{\circ}\tan1^{\circ} + \sin4^{\circ}\tan1^{\circ} + \cdots + \sin178^{\circ}\tan1^{\circ})\).
- Given \(\sin \theta + \cos \theta = \frac{\sqrt{2}}{3}\) and \(\frac{\pi}{2} < \theta < \pi\), find the value of \(\tan \theta - \cot \theta\).
- Find the value of \( \sin\frac{\pi}{16} \left( \sin^4\frac{\pi}{16} - \cos^4\frac{\pi}{16} \right) \cos\frac{\pi}{16} \).

## cluster 28 -- 587 prompts -- digits, digit, number, sum, decimal, base, times, integer
- Find the last two digits of \(3^{123456789}\).
- Find the last two digits of \( 9^{9^{9^{9^{\cdots^9}}}} \).
- Let \( S(n) \) be the sum of the digits of any positive integer \( n \) in decimal notation. Let \( N = \sum_{k=10^{2003}}^{10^{2004}-1} S(k) \). Determine \( S(N) \).

## cluster 79 -- 579 prompts -- frac, value, numbers, real, sqrt, given, let, equations
- Given real numbers \(a\), \(b\), and \(c\) such that \(\{a, b, c\} = \{a^4 - 2b^2, b^4 - 2c^2, c^4 - 2a^2\}\) and \(a + b + c = -3\), find the values of \(a\), \(b\), and \(c\).
- Let \(a, b, c > 0\) be such that  \[ \frac{a^2 + b^2 + c^2 + ab + bc + c + a + 2}{a + b + c} = 1 + \sqrt{3}. \] Find the value of \(a + b + c\) when \(a = b = c\).
- If \(a\), \(b\), and \(c\) are different numbers and satisfy the equations \(a^3 + 3a + 14 = 0\), \(b^3 + 3b + 14 = 0\), and \(c^3 + 3c + 14 = 0\), find the value of \(\frac{1}{a} + \frac{1}{b} + \frac{1}{c}\).

## cluster 67 -- 573 prompts -- frac, expression, minimum, value, sqrt, calculate, let, real
- For \(a, b, c > 0\) and \(a + b + c = 3\), find the minimum value of the expression \[ \frac{1}{a(a^2 + bc + c^2)} + \frac{1}{b(b^2 + ca + a^2)} + \frac{1}{c(c^2 + ab + b^2)}. \]
- Let \( a, b, c > 0 \) such that \( a + b + c = 1 \). Calculate the minimum value of the expression:  \[ \frac{a + b}{c^2 + ab} + \frac{b + c}{a^2 + bc} + \frac{c + a}{b^2 + ca} - 8 - \frac{6abc}{ab + bc + ca - 3abc} \]
- Given \( a, b, c > 0 \) and \( a + b + c = 1 \), calculate the minimum value of the expression \[ \frac{a^2 + b^2 c}{b + c} + \frac{b^2 + c^2 a}{a + c} + \frac{c^2 + a^2 b}{a + b}. \]

## cluster 58 -- 569 prompts -- equations, solve, cases, begin, end, sqrt, frac, array
- Solve the system of equations: \[ \begin{cases} x^3 + x - 2 = y^3 + 3y^2 + 4y \\ x^5 + y^3 + 1 = 0 \end{cases} \]
- Solve the system of equations: \[ \begin{cases} y^3 + 3y^2z - z^3 - 6y^2 - 6yz + 3z^2 + 9y - 4 = 0 \\ y^2 + yz + z^2 - 3y - 3z + 2 = 0 \end{cases} \] where \( y, z \in \mathbb{R} \).
- Solve the system of equations: \[ \begin{cases} x^3 + y^2 = 2 \\ x^2 + xy + y^2 - y = 0 \end{cases} \]

## cluster 74 -- 568 prompts -- function, derivative, frac, int, differentiable, sin, mathbb, sqrt
- Let \( f(x) = \frac{1}{2}\left[f(xy) + f\left(\frac{x}{y}\right)\right] \) for all \( x \in \mathbb{R^+} \) such that \( f(1) = 0 \) and \( f'(1) = 2 \). Determine the function \( f(x) \).
- Find the function \( f(x) \) such that \( f(x) = x^2 - x \left( 2 \int_0^1 |f(t)| \, dt \right)^{\frac{1}{2}}. \)
- Find the derivative \( f'(x) \) where \( f(x) = (1+x)^{\frac{1}{x}} \).

## cluster 6 -- 561 prompts -- maximum, value, ldots, cdots, sum, leq, let, frac
- Given positive integers \(3 \leq m \leq n\) with \(m\) odd, and real numbers \(a_1, a_2, \cdots, a_s, b_1, b_2, \cdots, b_t\) such that \(-1 \leq a_i \leq 0 \leq b_j \leq 1\) for any \(i = 1, 2, \cdots, s\) and \(j = 1, 
- Given \( n > 1 \) and a real number \( s > 0 \), find the maximum value of \( x_1 x_2 + x_2 x_3 + \cdots + x_{n-1} x_n \) for non-negative real numbers \( x_i \) such that \( x_1 + x_2 + \cdots + x_n = s \).
- Determine the maximum value of \( c \) such that for all positive integers \( n \) and positive real numbers \( x_1, x_2, \ldots, x_n \), \[ \sum_{cyc} \frac{x_i}{x_{i+1} + x_{i+2}} \ge c \cdot n. \]

## cluster 43 -- 558 prompts -- frac, prove, cdots, geq, left, right, numbers, ldots
- Let \( n \) be a positive integer and \( a_{1}, a_{2}, \cdots, a_{n}, b_{1}, b_{2}, \cdots, b_{n}, A, \) and \( B \) be positive real numbers, satisfying: \[ a_{i} \leqslant b_{i}, \quad a_{i} \leqslant A \quad (i=1,2, \
- Let \( n \) be a positive integer, and \( a_1, a_2, \ldots, a_n \), \( b_1, b_2, \ldots, b_n \), \( A \), and \( B \) be positive real numbers such that: \[ a_i \leqslant b_i, a_i \leqslant A \quad (i=1,2, \ldots, n) \] 
- Given positive real numbers \(a_{1}, a_{2}, \cdots, a_{n}\) satisfying \(a_{1} + a_{2} + \cdots + a_{n} = 1\), prove that: $$ \left(a_{1} a_{2} + a_{2} a_{3} + \cdots + a_{n} a_{1}\right)\left(\frac{a_{1}}{a_{2}^{2} + a_

## cluster 57 -- 557 prompts -- letters, balls, ways, word, boxes, different, letter, number
- There are three $a$s, four $b$s, and two $c$s. Using these nine letters to form a permutation, if the condition is that the same letters cannot all be adjacent, how many such permutations are there?
- We have \( n \) objects to place in \( n \) positions. However, some objects are identical. There are \( k \) different types of objects, and there are \( n_{i} \) objects of the \( i^{\text{th}} \) type. Thus, \( \sum_{
- How many arrangements can be made with 5 red balls ($R_1, R_2, R_3, R_4, R_5$) and 2 white balls ($W_1, W_2$) such that the two ends are occupied by red balls, the white balls are not next to each other, and $R_1$ and $W

## cluster 48 -- 556 prompts -- polynomial, roots, polynomials, given, degree, coefficients, real, frac
- Given the polynomial \( f(x) = x^4 + x^2 + 1 \), find \( S = x_1^n + x_2^n + x_3^n + x_4^n \) where \( x_1, x_2, x_3, x_4 \) are the roots of \( f(x) \).
- Given the polynomial \( P(x) = x^4 + ax^3 + bx^2 + cx + d \) with rational coefficients, where \( 1 + \sqrt{2} + \sqrt{3} \) is a root, find \( a + b + c + d \).
- Let \( P(x) \) be a polynomial of degree 3 with roots \( x_1, x_2, x_3 \). Given the conditions: \[ \frac{P\left(\frac{1}{3}\right) - P\left(\frac{-1}{3}\right)}{P(0)} = 8, \] \[ \frac{P\left(\frac{1}{4}\right) - P\left(

## cluster 47 -- 548 prompts -- int, integral, sin, evaluate, cos, frac, tan, sqrt
- Evaluate the integral \( \int_0^{\frac{\pi}{2}} (x \cos x + \sin^2 x) \sin x \, dx \).
- Evaluate the integral $\int_{0}^{\frac{\pi}{2}} \frac{\cos^2 x + \sin x \cos x}{1 + \sin 2x} \, dx$.
- Evaluate the integral $\int _{0}^{\frac{\pi }{2}}[\cos^{2} (\cos x)+\sin^{2} (\sin x)] \, dx$.

## cluster 96 -- 547 prompts -- angle, circ, abcd, measure, point, angles, trapezoid, parallelogram
- Quadrilateral \(ABCD\) has side lengths \(AB = 27\), \(BC = 21\), \(CD = 19\), and \(AD = \sqrt{649}\). Diagonals \(AC\) and \(BD\) intersect at point \(E\). Find the measure of \(\angle AEB\).
- In quadrilateral \(ABCD\), \(AD\) is parallel to \(BC\) and \(AB = AC\). Point \(F\) is on \(BC\) such that \(DF\) is perpendicular to \(BC\). \(AC\) intersects \(DF\) at \(E\). Given that \(BE = 2DF\) and \(BE\) bisects
- In trapezoid \(ABCD\) with \(AD\) and \(BC\) as the bases, \(\angle ABC = 90^\circ\). Point \(E\) is the intersection of \(AB\) and \(CD\), point \(O\) is the intersection of the diagonals, and \(M\) is the midpoint of \

## cluster 73 -- 534 prompts -- sqrt, frac, value, expansion, coefficient, real, cdots, given
- Given \((x+1)^{2002} = a_{0} + a_{1} x + a_{2} x^{2} + \cdots + a_{2002} x^{2002}\), find the value of \(a_{1} + a_{4} + a_{7} + \cdots + a_{2002}\).  A. \(\frac{2^{2002}-1}{3}\)   B. \(\frac{2^{2002}+2}{3}\)   C. \(2^{2
- Given \( x = \frac{1}{2 - \sqrt{3}} \), find the value of: \[ x^6 - 2\sqrt{3}x^5 - x^4 + x^3 - 4x^2 + 2x - \sqrt{3} \]
- Let \( C \) be the coefficient of \( x^2 \) in the expansion of the product \[(1 - x)(1 + 2x)(1 - 3x) \cdots (1 + 14x)(1 - 15x).\] Find \( |C| \).

## cluster 37 -- 523 prompts -- int, integral, frac, sin, cos, infty, sqrt, calculate
- Calculate the integral \( \int_{0}^{1}\int_{0}^{1}\int_{0}^{1}{x_1(x_3 - x_1)(x_2 - x_3)^m dx_1dx_2dx_3} \) where \( m \in \mathbb{N^{*}} \).
- Find \( I = \int_0^{\infty} x^{-\frac{1}{2}} e^{ax} \cos(bx) \, dx \) where \( a < 0 \).
- Evaluate the integral \(\int^{\pi/2}_{0}cz^{2}\sec^{3}{\theta}e^{-cz\sec{\theta}}d\theta\), where \(c\) and \(z\) are constants.

## cluster 91 -- 508 prompts -- group, mathbb, order, let, ring, subgroups, elements, subgroup
- Let \( (G, \cdot) \) be a finite group of order \( 4n + 2 \) for some \( n \in \mathbb{N} \). Suppose \( G \) has an automorphism \( f \) such that for any \( x \in G \), \( f(x) = g(x) \cdot h(x) \) for some automorphis
- Let \( K \) be a finite field. Find the number of elements in the groups \( GL(n, K) \), \( SL(n, K) \), \( PGL(n, K) \), and \( PSL(n, K) \), where \( PGL(n, K) = GL(n, K) / Z(GL(n, K)) \) and \( PSL(n, K) = SL(n, K) / 
- Let \( G \) be a group, and let \( g_{i} \in G \setminus \{ e \} \) for \( i \in \{ 1, 2, 3 \} \) where \( e \) is the identity element of \( G \), such that  \[ g_{k} \cdot g_{k+1 \pmod 3} = g_{k+2 \pmod 3} \] for all \

## cluster 1 -- 499 prompts -- function, value, minimum, maximum, frac, mathbb, int, sin
- For the function \( f(x) = |x^2 + ax + b| \), let \( M \) be the maximum value of \( f(x) \) on the interval \([-1, 3]\). Find the minimum possible value of \( M \).
- Consider the function \( f: \mathbb{R} \rightarrow \mathbb{R} \) defined by \( f(a) = \max_{x \in \mathbb{R}} \left| \frac{3}{4 + \cos x} + \cos x + a \right| \) for every real number \( a \). Find the minimum value of \
- Given the function \( f(x) = x^2 + bx + c \), find the minimum value of \( M \), where \( M \) is the maximum of \( |f(x)| \) for \( -1 \leq x \leq 1 \).

## cluster 99 -- 490 prompts -- integers, positive, integer, divides, pairs, mid, frac, cdots
- Find all positive integers \( n \) such that \( 3 \mid (2^n - 1) \) and \( \frac{2^n - 1}{3} \mid 4m^2 + 1 \) for some integer \( m \).
- Find all positive integers \( m \) and \( n \) (with \( m, n \geq 2 \)) such that for every \( a \in \{1, 2, \ldots, n\} \), \( a^n \equiv 1 \pmod{m} \).
- Find all positive integers \( m \) and \( n \) such that \((n-1)! + 1 = n^m\).

## cluster 65 -- 488 prompts -- lim, limit, frac, evaluate, sin, infty, rightarrow, left
- Evaluate the limit \( \lim_{x \to 0} \left[ x^2 \left( \cos{\frac{1}{x}} - \cos{\frac{3}{x}} \right) \right] \).
- Evaluate the limit \(\lim_{x\rightarrow 0}\left(\frac{2+e^{\frac{1}{x}}}{1+e^{\frac{4}{x}}}+\frac{\sin x}{|x|}\right)\).
- Evaluate the limit as \( x \) approaches 0 of \( \frac{\ln(1 - x) \sin(x)}{1 - \cos^2(x)} \).

## cluster 14 -- 480 prompts -- minimum, value, frac, sqrt, real, numbers, let, given
- Let \( x > 1 \), \( y > 1 \), \( z > 1 \) and \( x + y + z = xyz \). Find the minimum value of \( A = \frac{y-2}{x^2} + \frac{z-2}{y^2} + \frac{x-2}{z^2} \).
- Find the minimum value of  \[ x^2 + y^2 + z^2 + \frac{1}{xy + yz + zx} \] when $x - y - z = -4$ and $x, y, z$ are positive real numbers.
- Given \( x, y, z \in \mathbb{R}^+ \) and \( x^2 + y^2 + z^2 = 1 \), find the minimum value of \( \frac{yz}{x} + \frac{xz}{y} + \frac{xy}{z} \).

## cluster 40 -- 478 prompts -- sphere, radius, cone, volume, cylinder, surface, height, base
- a) The radius of a right circular cylinder and its height are equal to $R$. Consider a sphere with radius $R$ centered at the center $O$ of the lower base of the cylinder and a cone with its vertex at $O$, whose base is 
- Inside the cube \(ABCD A_{1}B_{1}C_{1}D_{1}\) there is a sphere with center \(O\) and radius 10. The sphere intersects the face \(AA_{1}D_{1}D\) in a circle of radius 1, the face \(A_{1}B_{1}C_{1}D_{1}\) in a circle of r
- Given a cube-shaped box with a side length equal to the diameter of a larger sphere, a smaller sphere is placed in one corner of the box such that it fits exactly in the space left after the larger sphere is placed there

## cluster 33 -- 469 prompts -- natural, numbers, number, divisible, divides, frac, sum, pairs
- Find all natural numbers \( n \) such that \( n \) divides \( 2^n + 1 \).
- Find all natural numbers \( n \) such that \( n \) divides \( 2^n + 2 \).
- Find all natural numbers \( n > 1 \) such that \( n \) divides \( 2^n + 1 \).

## cluster 52 -- 461 prompts -- int, integral, evaluate, infty, frac, left, right, cos
- Evaluate the integral \( \int_{0}^{+\infty}\frac{\ln(x^2+1)}{x^2+1} \, dx \).
- Evaluate the integral $$\int_{0}^{\infty} \frac{\ln(x)}{e^{x} + e^{-x} + 1} \,dx.$$
- Evaluate the integral $$\int_0^\infty\frac{e^{-x}\ln{x}}{(1+e^{-x})^2}dx.$$

## cluster 7 -- 460 prompts -- integral, int, evaluate, frac, sqrt, calculate, left, right
- Evaluate the integral \(\int \frac{dx}{x^{2}+1-x\sqrt{x^{2}+1}}\).
- Evaluate the integral \(\int \frac{1}{x^{2}\sqrt{(1+x^{2})^{3}}} \,dx\).
- Evaluate the integral $\int\frac{dx}{(x^{2}-x+1)(\sqrt{x^{2}+x+1})}$.

## cluster 66 -- 460 prompts -- largest, integer, positive, integers, value, frac, possible, number
- Suppose that \((a_1, b_1), (a_2, b_2), \dots, (a_{100}, b_{100})\) are distinct ordered pairs of nonnegative integers. Let \(N\) denote the number of pairs of integers \((i, j)\) satisfying \(1 \leq i < j \leq 100\) and 
- Given a positive integer \( n \), find the largest positive integer \( k \) such that \( 2^k \) divides \( (n + 1)(n + 2) \cdots (n + n) \).
- Find the largest integer \( n \) such that \(\frac{(n-2)^{2}(n+1)}{2n-1}\) is an integer.

## cluster 86 -- 459 prompts -- tetrahedron, pyramid, base, volume, regular, edge, plane, edges
- Calculate the volume of the tetrahedron with vertices at the points $A_{1}, A_{2}, A_{3}, A_{4}$ and its height, dropped from vertex $A_{4}$ onto the face $A_{1} A_{2} A_{3}$.  $A_{1}(4, -1, 3)$  $A_{2}(-2, 1, 0)$  $A_{3
- In the triangular pyramid \( P-ABC \), given \( BC=3 \), \( CA=4 \), \( AB=5 \). If the dihedral angles between the three lateral faces and the base face are all \( 45^{\circ} \), find the volume of the triangular pyrami
- As shown in the figure, in the cuboid \(ABCD-A_1 B_1 C_1 D_1\), it is known that \(AB = BC = 6\), \(AA_1 = 2\), points \(M\) and \(N\) are on edges \(DA\) and \(DC\) respectively, and the dihedral angle \(D_1 - MN - D\) 

## cluster 27 -- 456 prompts -- expression, simplify, frac, sqrt, factor, left, right, cdot
- Simplify the expression: \(\frac{2b + a - \frac{4a^2 - b^2}{a}}{b^3 + 2ab^2 - 3a^2b} \cdot \frac{a^3b - 2a^2b^2 + ab^3}{a^2 - b^2}\).
- Simplify the expression \(\frac{2(\sqrt{2} + \sqrt{6})}{3(\sqrt{2 + \sqrt{3}})}\).
- Simplify the expression:   \[ \frac{\sqrt{3}\left(a - b^2 \right) + \sqrt{3} b \sqrt[3]{8 b^3}}{\sqrt{2 \left(a - b^2 \right)^2 + (2 b \sqrt{2 a})^2}} \cdot \frac{\sqrt{2 a} - \sqrt{2 c}}{\sqrt{\frac{3}{a}} - \sqrt{\frac

## cluster 50 -- 452 prompts -- perfect, square, integers, squares, positive, integer, natural, numbers
- Find all positive integers \( n \) such that \( (1+n)(1+n^2) \) is a perfect square.
- Find all integers \( n \) such that \( n(n+1) \) is a perfect square.
- Find all positive integers $n$ such that $(1+n)(1+n^2)$ is a perfect square.

## cluster 85 -- 451 prompts -- sequence, term, ldots, terms, number, sequences, numbers, permutations
- Determine the number of sequences \(a_1, a_2, \ldots, a_{10}\) such that: - \(a_i = 0\) or \(1\) for all \(i = 1, 2, \ldots, 10\), - \(a_i \cdot a_{i+1} = 0\) for all \(i = 1, 2, \ldots, 9\), - \(a_i \cdot a_{i+2} = 0\) 
- Find the general term \( a_n \) of the sequence \( 5, 8, 26, 48, 122, \ldots \)
- Find the number of sequences \((A(1), A(2), A(3), A(4), A(5), A(6), A(7), A(8))\) where: - \(A(1)\) can be 1, 2, 3, 4, or 5 - \(A(2)\) can be 1, 2, 3, 4, 5, or 6 - \(A(3)\) can be 1, 2, 3, 4, 5, 6, or 7 - \(A(4)\) can be

## cluster 90 -- 450 prompts -- integers, positive, pairs, integer, frac, divides, triples, mid
- Find all positive integers \( a \), \( b \), and \( c \) (where \( a, b, c \geq 2 \)) such that \( a^b + 1 = (a + 1)^c \).
- Find all positive integers \(a, b, c\) such that \(a^2 = 4(b + c)\) and \(a^3 - 2b^3 - 4c^3 = \frac{1}{2}abc\).
- Find all positive integers \(a\) and \(b\) such that: \[ \frac{ab}{ab+1} + \frac{a^2b}{a^2+b} + \frac{b^2a}{b^2+a} = \frac{a+b+ab}{2} \]

## cluster 94 -- 447 prompts -- solutions, equation, number, real, does, integer, frac, positive
- Find the number of integer solutions to the equation \[x_1 + x_2 + x_3 + x_4 + x_5 = n\] satisfying \[0 \le x_1 \le x_2 \le x_3 \le x_4 \le x_5 \le n.\]
- Find the number of solutions to the equation \(a_1 + a_2 + \ldots + a_r = n\) where \(r, n, a_i \in \mathbb{N}\).
- Find the number of solutions in positive integers \( (k; a_1,a_2,\ldots,a_k; b_1,b_2,\ldots,b_k) \) to the equation \[ a_1(b_1) + a_2(b_1 + b_2) + \cdots + a_k(b_1 + b_2 + \ldots + b_k) = 7. \]

## cluster 95 -- 447 prompts -- frac, value, numbers, real, given, sqrt, equations, equation
- Given that \(x^2 + y^2 + xy = 3\), \(y^2 + z^2 + yz = 4\), and \(z^2 + x^2 + xz = 1\), where \(x, y, z\) are nonnegative real numbers, find the value of \(x + y + z\).
- Given \( x, y, z \in \mathbb{C} \) such that \( x^2 + y^2 + z^2 = 3 \), \( x + y + z = 2 \), and \( xyz = 4 \), find the value of \( \frac{1}{xy + z - 1} + \frac{1}{yz + x - 1} + \frac{1}{zx + y - 1} \).
- Given that \( x \) and \( y \) are real numbers satisfying the equation \( (2x+1)^2 + y^2 + (y-2x)^2 = \frac{1}{3} \), find \( x + y \).

## cluster 69 -- 434 prompts -- prime, numbers, primes, number, perfect, pairs, integers, equation
- Find all prime numbers \( p \) and \( q \) such that \( (p+1)^q = k^2 \), where \( k \) is an integer.
- Find all prime numbers \( p \) and \( q \) such that \( p(p-1) = q(q^2 + 3) \).
- Find all prime numbers \( p \) such that \( p + q = (p - q)^3 \).

## cluster 5 -- 431 prompts -- point, ant, moves, vertex, starts, jumps, step, unit
- A robot is moving through the edges of a 4-dimensional unit cube (4-cube) starting from the vertex $(0,0,0,0)$. Each turn consists of moving to an adjacent vertex. In how many ways can the robot return to $(0,0,0,0)$ aft
- Ten pairwise distinct points \( T_1, T_2, \ldots, T_{10} \) are chosen in space and some of them are connected by segments without intersections. A beetle sitting at point \( T_1 \) can move along the segments to point \
- An ant moves along the edges of a regular octahedron, starting at vertex $A$. Each move takes one minute, and the ant chooses a new random edge, different from the previous one, at each vertex. After 4 minutes, what is t

## cluster 25 -- 413 prompts -- sum, evaluate, frac, infty, binom, series, infinite, left
- Evaluate the sum: $$\sum_{n=1}^{\infty} \frac{(-1)^{n+1}}{3^n(2n-1)}$$
- Evaluate the sum $$\sum_{n=1}^{\infty}{\frac{1}{(2n-1)^2(2n+1)^2}}.$$
- Evaluate the sum \( \sum_{n=0}^{\infty} \sum_{k=1}^{n+2} \frac{1}{k(n+2)(n!)} \).

## cluster 92 -- 402 prompts -- solve, equation, integers, mathbb, positive, numbers, natural, set
- Solve the equation \( x^n + y^n = (x-y)^{n+1} \) for integers \( x \) and \( y \) and \( n \in \mathbb{N} \).
- Solve the equation $(x-y)^3 = (x+y-2)^2 + xy$ in the set of integers $\mathbb{Z}$.
- Solve the equation \(x^3 = 2y^2 + 1\) in the set of integers \(\mathbb{Z}\).

## cluster 12 -- 395 prompts -- solutions, equation, integer, positive, integers, solution, satisfy, frac
- Find all integer solutions to the equation  $$ y^{2}+y = x^{4}+x^{3}+x^{2}+x $$
- Find all integer solutions to the equation \((x+y)^x - x^{(x+y)} = 2\).
- Find all positive integer solutions to the equation \(X^2 = 2Y^2 + Z^3\) where \(\gcd(X, Y) = 1\).

## cluster 62 -- 395 prompts -- continuous, mathbb, functions, function, rightarrow, int, infty, frac
- Find all continuous functions \( f: \mathbb{R} \rightarrow \mathbb{R} \) such that  \[ f(x - f(x)f(y)) + f(x)f(y+1) = 2x \] for every real numbers \( x \) and \( y \).
- Find all continuous functions \( f : \mathbb{R}_+ \longrightarrow \mathbb{R}_+ \) such that for all \( x, y > 0 \),  \[ f(xf(y)) + f(yf(x)) = 1 + f(x + y). \]
- Find all continuous functions \( f: \mathbb{R} \to \mathbb{R} \) such that \[ f(x^2 + f(y)) = (f(x))^2 + f(y^2) + 2f(xy), \quad \forall x, y \in \mathbb{R}. \]

## cluster 98 -- 394 prompts -- integers, positive, pairs, satisfy, equation, triples, mathbb, satisfying
- Find all positive integers \( x, y, z \) such that \[ (x+y)^2 + 3x + y + 1 = z^2. \]
- Find all pairs of positive integers \( (x, y) \) such that \( x^3 + y^3 = (x + y)^2 + (xy)^2 \).
- Find all positive integers \( x, y, z \) such that \( x^2 + y^2 = z^2 + 3 \).

## cluster 77 -- 377 prompts -- remainder, divided, number, let, cdots, cdot, integer, sum
- Find the remainder when a number \( N \) is divided by 84, given that when \( N \) is divided by 3, 4, and 7, the remainders are 2, 1, and 4, respectively.
- Find the remainder when \( k = 2^{2017} + 3^{2017} + 4^{2017} + \ldots + 2000^{2017} + 2001^{2017} \) is divided by \( 77 \).
- Determine the remainder $N$ when $1 + 7 + 7^2 + \ldots + 7^{2004}$ is divided by $1000$.

## cluster 11 -- 342 prompts -- differential, equation, solve, frac, solution, initial, condition, partial
- Solve the differential equation \( x\frac{d^2y}{dx^2} - (2x-1)\frac{dy}{dx} + (x-1)y = 0 \).
- Find the particular solution of the differential equation \( x^2 y'' - xy' + y = 2x \) with the initial conditions \( y(1) = 0 \) and \( y'(1) = 1 \).
- Solve the differential equation \( x \, dx + y \, dy + (x^2 + y^2) \, dy = 0 \).

## cluster 55 -- 337 prompts -- log, solve, frac, equation, sqrt, left, right, value
- Solve the equation \(\log_{2}(x+3) + \log_{2}(x-1) = 3\).
- Solve for \( x \) in the equation \(\log_{2}{x} + (\log_{2}{x})^2 + (\log_{2}{x})^3 = 0.5\).
- Solve for $x$: \[ \log_2 (x-5) + \log_2 (x-3) = \log_5 (5^3) \]

## cluster 80 -- 331 prompts -- random, distribution, variables, independent, variable, density, probability, function
- Suppose \( X_1, X_2, \ldots \) are independent and identically distributed random variables with \( P(X_i = 1) = \frac{1}{4} \), \( P(X_i = -1) = \frac{1}{4} \), and \( P(X_i = 0) = \frac{1}{2} \) for all \( i = 1, 2, \l
- Let \(X, X_1, \ldots, X_n\) be independent and identically distributed uniform random variables over \((0,1)\). Let \(X_{(1)}, \ldots, X_{(n)}\) be the order statistics of \(X_1, \ldots, X_n\). Determine \(P(X > X_{(n)})
- Let \( X_1, \ldots, X_n \) be i.i.d. random variables with \( P(X_i = -1) = P(X_i = 1) = \frac{1}{2} \). Let \( S_n = X_1 + \cdots + X_n \) for \( n \geq 1 \). Let \( N = \min\{n \geq 1 : S_n = 0\} \). Find \( P(N = 2k, 

## cluster 49 -- 328 prompts -- sin, cos, solve, equation, tan, frac, sqrt, left
- Solve the equation \(\cos 3x + \sin 2x - \cos x - 1 = 0.\)
- Solve the trigonometric equation \(\sin(2x) + \cos(x) = 0\).
- Solve the equation \(\cos (\cos (\cos (\cos x))) = \sin (\sin (\sin (\sin x)))\).

## cluster 42 -- 316 prompts -- chessboard, squares, times, square, board, placed, rooks, number
- Find the number of ways to place \( K \) rooks on an \( N \times N \) chessboard such that no two rooks attack each other. All rooks are considered identical.
- a) What is the maximum number of rooks that can be placed on a chessboard of $n^{2}$ squares so that no two rooks threaten each other? In how many different ways can this be done?  b) What is the minimum number of rooks 
- On an 8x8 chessboard, how many ways can 8 rooks be placed such that no two rooks attack each other, given that rooks cannot be placed on the cells of 2 main diagonals?

## cluster 83 -- 313 prompts -- complex, frac, number, numbers, left, right, let, value
- Let \( z_1, z_2, z_3 \) be complex numbers such that \( |z_1| = |z_2| = |z_3| = 1 \) and  \[ \frac{z_1^2}{z_2 z_3} + \frac{z_2^2}{z_3 z_1} + \frac{z_3^2}{z_1 z_2} = -1. \] Determine the value of \( |z_1 + z_2 + z_3| \). 
- Find the complex number $z$ such that \[|z - 1| = |z + 3| = |z - i|.\]
- Given complex numbers \(A(z_1)\), \(B(z_2)\), and \(C(z_3)\) satisfying \(|z - \sqrt{3}i| = 1\) and \(3z_1 + \sqrt{3}i = 2z_2 + 2z_3\), find the value of \(\frac{z_2 - \sqrt{3}i}{z_3 - \sqrt{3}i}\).

## cluster 26 -- 308 prompts -- polynomials, coefficients, real, mathbb, polynomial, satisfying, satisfy, frac
- Find all polynomials \( P(x) \) with real coefficients that satisfy the condition: \[ P(x)P(2x^2-1) = P(x^2)P(2x-1) \] for all \( x \in \mathbb{R} \).
- Find all polynomials \( P(x) \) such that \[ (x + 1)P(x - 1) + (x - 1)P(x + 1) = 2xP(x) \] for all real numbers \( x \).
- Find all polynomials with real coefficients \( P \) such that \[ P(x)P(2x^2-1) = P(x^2)P(2x-1) \] for every \( x \in \mathbb{R} \).

## cluster 78 -- 306 prompts -- lfloor, rfloor, left, right, frac, sqrt, sum, denotes
- Find all real numbers \(n\) such that \(\left\lfloor \frac{n}{2} \right\rfloor + \left\lfloor \frac{n}{3} \right\rfloor + \left\lfloor \frac{n}{5} \right\rfloor = 1\), where \(\left\lfloor x \right\rfloor\) denotes the g
- Solve the equation: \(\left\lfloor \frac{1}{x} \right\rfloor + \left\lfloor \frac{4}{x} \right\rfloor + \cdots + \left\lfloor \frac{n^2}{x} \right\rfloor = n\), where \(\left\lfloor \cdot \right\rfloor\) denotes the inte
- Find \( x \) such that \( \left\lfloor \frac{x}{2} \right\rfloor + \left\lfloor \frac{x}{3} \right\rfloor = 17 \).

## cluster 19 -- 303 prompts -- ordered, pairs, integers, satisfy, triples, number, positive, leq
- Find the number of ordered triples of positive integers \( (a, b, c) \) that satisfy \[ \frac{a^2 + b^2 - c^2}{ab} + \frac{b^2 + c^2 - a^2}{bc} + \frac{c^2 + a^2 - b^2}{ca} = 2 + \frac{96}{abc}. \]
- Given positive integers \(a, b,\) and \(c\) that satisfy \(2017 \geq 10a \geq 100b \geq 1000c\), determine how many such ordered triples \((a, b, c)\) exist.
- Determine all ordered pairs that satisfy \((x - y)^2 + x^2 = 25\), where \(x\) and \(y\) are integers, and \(x \geq 0\). The number of different values of \(y\) that occur is: (A) 3   (B) 4   (C) 5   (D) 6   (E) 7

## cluster 82 -- 300 prompts -- area, region, bounded, axis, curve, volume, leq, enclosed
- Find the area of the region bounded by the curves \(x^2 + y^2 = 2x\), \(x^2 + y^2 = 4x\), \(y = x\), and \(y = 0\).
- Find the area bounded by the curves \( y = \frac{1}{2} \cos(2x) \), \( y = 0 \), \( x = -\frac{\pi}{2} \), and \( x = \frac{\pi}{2} \).
- Find the area of the surface \( z = xy \) within the region \( x^2 + y^2 \leq 1 \).

## cluster 21 -- 293 prompts -- expression, minimum, frac, value, sqrt, real, numbers, calculate
- Given positive numbers \(x\), \(y\), and \(z\) such that \(xyz + x + z = y\), find the minimum value of the expression: \[ \frac{2}{1+x^2} + \frac{2}{1+y^2} + \frac{3}{1+z^2} \]
- Let \( x, y, z \geq 0 \). Calculate the minimum value of the expression: \[ -2 + \frac{x^2 + yz}{2x^2 + yz} + \frac{y^2 + xz}{2y^2 + xz} + \frac{z^2 + xy}{2z^2 + xy} \]
- Let \( x, y, z \) be positive real numbers. Find the minimum value of the expression  \[ \frac{xyz(x^2 + y^2 + z^2 + 1)}{(x + y + z - xyz)(3xyz - 1)} \]

## cluster 51 -- 226 prompts -- graph, vertices, edges, number, vertex, connected, edge, graphs
- Graph \( G \) contains \( 2n-1 \) vertices. It is known that if we delete any arbitrary vertex in \( G \), we are still able to find a \( K_n \) subgraph. Let \( f(n) \) be the minimum number of \( K_{n+1} \) subgraphs t
- Let \( G \) be an even graph with an even number of vertices \( |V| \). Consider a partition of \( V \) into two non-empty subsets \( V_1 \) and \( V_2 \) such that the induced subgraph of \( G \) on each subset is also 
- Let \( G = (V, E) \) be a graph and let \( A, B \subseteq V \). The minimum number of vertices that separate \( A \) and \( B \) in \( G \) is equal to the maximum number of disjoint \( A-B \) paths in \( G \).  Given \(

## cluster 0 -- 212 prompts -- range, function, real, frac, cos, sin, values, determine
- Given that \( x \) and \( y \) are real numbers and \( x^{3} + y^{3} = 2 \), determine the range of values for \( x + y \): (A) \((-∞, 2)\). (B) \([- \sqrt[3]{2}, \sqrt[3]{2}]\). (C) \((0, 2]\). (D) \((2, +∞)\).
- Find the range of the function \( \frac{1}{2bx - (x^2 + b^2 + \sin^2 x)} \) for \( x \in [-1, 0] \) and \( b \in [2, 3] \).
- Given four positive numbers \(a\), \(b\), \(c\), and \(d\), determine the range of the real function \(f(x, y) = cx + dy\) where the real pair \((x, y)\) satisfies the inequality \(x^2 + y^2 \leq 2(ax + by)\).

## cluster 71 -- 209 prompts -- cards, card, deck, probability, number, numbered, numbers, hand
- You draw 4 cards from a standard deck of 52 cards. What is the probability that all of these cards have different denominations and there are no neighboring denominations (e.g., an 8 and a 9, a 10 and a Jack, or a queen 
- Bill has a set of 6 black cards and a set of 6 red cards. Each card has a number from 1 through 6, such that each of the numbers 1 through 6 appears on 1 black card and 1 red card. Bill shuffles all 12 cards, turns over 
- You have a deck of 20 cards, with 8 blue, 5 red, and the rest green. If you randomly pick 5 cards from the deck, what is the probability that you will have at least one card of each color?

## cluster 64 -- 197 prompts -- cities, city, roads, road, country, connected, routes, travel
- In a country with 100 cities, some pairs of cities are connected by roads. For every set of four cities, there are at least two roads between them. It is known that there is no route that visits each city exactly once. P
- A country has a total of 1001 cities, and there is a one-way road connecting every pair of cities. Each city has exactly 500 outgoing roads and 500 incoming roads. A region within this country is designated to include 66
- In a country, there are 110 cities. Between each pair of cities, there is either a road or no road.  A driver starts in a city with exactly one road leading out of it. After traveling along this road, he arrives at a sec

## cluster 46 -- 181 prompts -- common, greatest, divisor, gcd, integers, lcm, positive, numbers
- Given \(A_n = 2^{3n} + 3^{6n+2} + 5^{6n+2}\) for positive integer \(n\), find the greatest common divisor (GCD) of all \(A_i\).
- Determine the greatest common divisor (gcd) of all natural numbers \( n > 1 \) such that \( n \) divides \( 2^n + 1 \). (Conjecture: 3)
- Let \( n \) be a positive integer and \( d \) be the greatest common divisor of \( n^2 + 1 \) and \( (n+1)^2 + 1 \). Find all the possible values of \( d \). Justify your answer.
