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
import java.util.List;
import java.util.UUID;

abstract class ThingDistribution<T extends DistributableThing> implements Distribution<T> {
	private static class Share<T> {
		private final double occurence;
		private final T thing;
		private double startParameter;
		private double endParameter;

		protected Share(double occurence, T thing) {
			this.occurence = occurence;
			this.thing = thing;
		}

		public final double getOccurence() {
			return this.occurence;
		}

		public final T getThing() {
			return this.thing;
		}

		public boolean parameterMatches(double t) {
			return (this.startParameter - t) * (this.endParameter - t) <= 0.;
		}

		public final void setStartParameter(double startParameter) {
			this.startParameter = startParameter;
		}

		public final void setEndParameter(double endParameter) {
			this.endParameter = endParameter;
		}

	}
	
	private final Comparator<Share<T>> shareSorter = (a, b) -> {
		return a.getThing().getUuid().compareTo(b.getThing().getUuid());
	};
	
	private List<Share<T>> data = new ArrayList<>();
	
	protected ThingDistribution() {
	}
	
	protected void addShare(double occurence, T thing) {
		data.add(new Share<T>(occurence, thing));
		makeSharesUsable();
	}

	private void makeSharesUsable() {
		data.sort(shareSorter);
		
		final double total = data.stream().mapToDouble(Share::getOccurence).sum();
		if (total <= 0.) {
			throw new RuntimeException("Total shares in thing distribution must be greater than zero.");
		}

		double runningTotal = 0.;
		for (Share<T> item : data) {
			item.setStartParameter(runningTotal);
			final double parameterRange = item.getOccurence() / total;
			runningTotal += parameterRange;
			item.setEndParameter(runningTotal);
		}
		
		// account for fp arithmetic making last share end parameter < 1
		data.get(data.size() - 1).setEndParameter(1.);
	}
	
	@Override
	public final T getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new IllegalArgumentException(
					"In ThingDistribution, parameter passed to getValue must be in range [0, 1]");
		}
		
		for (Share<T> share : data) {
			if (share.parameterMatches(t)) {
				return share.getThing();
			}
		}

		return null;
	}

	@Override public abstract String getName();

	@Override public abstract UUID getUuid();

}
