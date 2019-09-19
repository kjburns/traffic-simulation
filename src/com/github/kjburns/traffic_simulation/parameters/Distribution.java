package com.github.kjburns.traffic_simulation.parameters;

import java.util.UUID;

/**
 * A distribution that provides values over the domain of parameters [0, 1].
 * @author Kevin J. Burns
 *
 * @param <T>
 */
public interface Distribution<T> {
	/**
	 * Gets the value of the distribution at the provided parameter.
	 * @param t A parameter in the range [0, 1]. Implementors are strongly
	 * encouraged to throw a runtime exception if the parameter is outside
	 * the legal range.
	 * @return
	 */
	T getValue(double t);
	/**
	 * Gets the name of this distribution.
	 * @return
	 */
	String getName();
	/**
	 * Gets this distribution's UUID.
	 * @return
	 */
	UUID getUuid();
}
