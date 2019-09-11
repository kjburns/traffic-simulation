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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

public class ConnectorLinkSelectionBehaviorDistribution 
		extends AbstractDistribution<ConnectorLinkSelectionBehaviorEnum> {
	public static class Factory {
		public static class Builder {
			private final String name;
			private final UUID uuid;
			private final Map<ConnectorLinkSelectionBehaviorEnum, Double> shares = new HashMap<>();
			
			public Builder(String _name, UUID _uuid) {
				name = _name;
				uuid = _uuid;
			}
			
			public void setShare(ConnectorLinkSelectionBehaviorEnum behavior, double share) {
				shares.put(behavior, share);
			}
			
			public Distribution<ConnectorLinkSelectionBehaviorEnum> build() {
				final ConnectorLinkSelectionBehaviorDistribution ret = 
						new ConnectorLinkSelectionBehaviorDistribution(name, uuid);
				
				final double total = shares.values().stream().mapToDouble((value) -> {
					return value;
				}).sum();
				
				if (total == 0.) {
					throw new RuntimeException("Total of shares in distribution must be greater than zero.");
				}

				double runningTotal = 0.;
				final List<ConnectorLinkSelectionBehaviorEnum> keysInOrder = 
						shares.keySet().stream().sorted((x, y) -> {
							return Integer.compare(x.ordinal(), y.ordinal());
						}).collect(Collectors.toList());
				
				for(ConnectorLinkSelectionBehaviorEnum key : keysInOrder) {
					final double proportion = shares.get(key) / total;
					final double nextRunningTotal = runningTotal + proportion;
					ret.sharesInOrder.add(new Share(runningTotal, nextRunningTotal, key));
					runningTotal = nextRunningTotal;
				}
				
				return ret;
			}
		}
		
		public static Builder createBuilder(String _name, UUID _uuid) {
			return new Builder(_name, _uuid);
		}
	}
	
	private static class Share {
		private final double startParameter;
		private final double endParameter;
		private final ConnectorLinkSelectionBehaviorEnum value;
		
		public Share(double startParameter, double endParameter, ConnectorLinkSelectionBehaviorEnum value) {
			this.startParameter = startParameter;
			this.endParameter = endParameter;
			this.value = value;
		}
		
		public boolean parameterMatches(double t) {
			return (this.startParameter - t) * (this.endParameter - t) <= 0.;
		}

		public final ConnectorLinkSelectionBehaviorEnum getValue() {
			return this.value;
		}
	}
	
	private final List<Share> sharesInOrder = new ArrayList<>();
	
	private ConnectorLinkSelectionBehaviorDistribution(String _name, UUID _uuid) {
		super(_name, _uuid);
	}

	@Override
	public ConnectorLinkSelectionBehaviorEnum getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new IllegalArgumentException(
					"Connector Link Selection Behavior Distribution: parameter must be in range [0, 1].");
		}
		
		for (Share share : sharesInOrder) {
			if (share.parameterMatches(t)) {
				return share.getValue();
			}
		}

		// should never happen
		return null;
	}
}
