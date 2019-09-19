package com.github.kjburns.traffic_simulation.parameters;

import java.util.UUID;

/**
 * Abstract implementation that enforces having a name and uuid in a distribution.
 * @author Kevin J. Burns
 *
 * @param <T> type of value in the distribution
 */
abstract class AbstractDistribution<T> implements Distribution<T> {
	private String name;
	private UUID uuid;
	
	protected AbstractDistribution(String _name, UUID _uuid) {
		name = _name;
		uuid = _uuid;
	}
	
	@Override
	public final String getName() {
		return name;
	}

	@Override
	public final UUID getUuid() {
		return uuid;
	}
}
