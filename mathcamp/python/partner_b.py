
import partner_a
from partner_a import get_prime_divisors

def get_factorization(n):
	divisors = get_prime_divisors(n)
	factorization = {}
	for d in divisors:
		m = n
		power = 0
		while m % d == 0:
			m = m / d
			power = power + 1
		factorization[d] = power
	return factorization
