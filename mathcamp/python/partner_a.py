

import math

def get_prime_divisors(n):
	return get_prime_divisors_helper(n, [])


def get_prime_divisors_helper(n, divisors):
	if n == 1:
		return divisors
	new_divisor = -1
	for i in range(2, int(n**.5) + 1):
		if n % i == 0:
			new_divisor = i
			break
	if new_divisor == -1:
		divisors.append(n)
		return divisors
	divisors.append(new_divisor)
	while n % new_divisor == 0:
		n = n / new_divisor
	return get_prime_divisors_helper(n, divisors)
