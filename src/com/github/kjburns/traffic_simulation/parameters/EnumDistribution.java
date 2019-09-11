/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.parameters;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

public abstract class EnumDistribution<T extends Enum<T>> extends AbstractDistribution<T> {
	protected static class Factory<T> {
		protected static abstract class Builder<T> {
			private final String name;
			private final UUID uuid;
			private final Map<T, Double> shares = new HashMap<>();
			
			public Builder(String _name, UUID _uuid) {
				name = _name;
				uuid = _uuid;
			}
			
			public void setShare(T behavior, double share) {
				shares.put(behavior, share);
			}
			
			protected void loadShares(EnumDistribution<? super T> distribution) {
				final double total = shares.values().stream().mapToDouble((value) -> {
					return value;
				}).sum();
				
				if (total == 0.) {
					throw new RuntimeException("Total of shares in distribution must be greater than zero.");
				}

				double runningTotal = 0.;
				@SuppressWarnings("rawtypes")
				final Comparator<T> sorter = (x, y) -> {
					return Integer.compare(((Enum)x).ordinal(), ((Enum)y).ordinal());
				};
				final List<T> keysInOrder = 
						shares.keySet().stream().sorted(sorter).collect(Collectors.toList());
				
				for(T key : keysInOrder) {
					final double proportion = shares.get(key) / total;
					final double nextRunningTotal = runningTotal + proportion;
					
					distribution.addShareToSortedList(new Share(runningTotal, nextRunningTotal, key));
					runningTotal = nextRunningTotal;
				}
			}
			
			public abstract Distribution<T> build();

			protected final String getName() {
				return this.name;
			}

			protected final UUID getUuid() {
				return this.uuid;
			}
		}
	}
	protected static class Share<T> {
		private final double startParameter;
		private final double endParameter;
		private final T value;
		
		public Share(double startParameter, double endParameter, T value) {
			this.startParameter = startParameter;
			this.endParameter = endParameter;
			this.value = value;
		}
		
		public boolean parameterMatches(double t) {
			return (this.startParameter - t) * (this.endParameter - t) <= 0.;
		}

		public final T getValue() {
			return this.value;
		}
	}
	
	private final List<T> enumValues = new ArrayList<>();
	private final List<Share<T>> sharesInOrder = new ArrayList<>();
	
	protected EnumDistribution(String _name, UUID _uuid, T[] _enumValues) {
		super(_name, _uuid);
		
		for (int i = 0; i < _enumValues.length; i++) {
			enumValues.add(_enumValues[i]);
		}
	}

	@Override
	public final T getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new IllegalArgumentException("Enum Distribution: parameter must be in range [0, 1].");
		}
		
		for (Share<T> share : sharesInOrder) {
			if (share.parameterMatches(t)) {
				return share.getValue();
			}
		}

		// should never happen
		return null;
	}
	
	protected final void addShareToSortedList(Share<T> share) {
		sharesInOrder.add(share);
	}
}
