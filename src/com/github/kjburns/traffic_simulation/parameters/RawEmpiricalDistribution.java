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
import java.util.Collections;
import java.util.List;
import java.util.UUID;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

final class RawEmpiricalDistribution extends AbstractDistribution<Double> {
	public enum AggressionTrend {
		/**
		 * Higher aggression causes higher values
		 */
		POSITIVE,
		/**
		 * Higher aggression causes lower values
		 */
		NEGATIVE;
	};
	
	public static class Factory {
		private static final String AGGRESSION_ATTR_VALUE_NEGATIVE = "negative";
		private static final String AGGRESSION_ATTR_VALUE_POSITIVE = "positive";
		private static final String DATAPOINT_VALUE_ATTR = "value";
		private static final String DATAPOINT_TAG = "dp";
		private static final String AGGRESSION_ATTR = "aggression";
		private static final String UUID_ATTR = "uuid";
		private static final String NAME_ATTR = "name";

		public static class Builder {
			private final String name;
			private final UUID uuid;
			private final List<Double> datapoints = new ArrayList<>();
			private AggressionTrend trend = AggressionTrend.POSITIVE;
			
			private Builder(String _name, UUID _uuid) {
				name = _name;
				uuid = _uuid;
			}
			
			public void addObservation(double observation) {
				datapoints.add(observation);
			}
			
			public RawEmpiricalDistribution build() {
				RawEmpiricalDistribution ret = new RawEmpiricalDistribution(name, uuid);
				
				Collections.sort(datapoints);
				ret.sortedObservations.addAll(datapoints);
				ret.reverse = (trend == AggressionTrend.NEGATIVE);
				
				return ret;
			}
			
			public void setAggressionTrend(AggressionTrend _trend) {
				if (_trend == null) {
					throw new IllegalArgumentException(
							"Aggression trend in raw empirical distribution must be one of the "
							+ "AggressionTrend enum values.");
				}
				
				trend = _trend;
			}
		}
		
		public static Builder createBuilder(String _name, UUID _uuid) {
			return new Builder(_name, _uuid);
		}
		
		public static RawEmpiricalDistribution fromXml(Element from) {
			final String name = from.hasAttribute(Factory.NAME_ATTR) ?
					from.getAttribute(Factory.NAME_ATTR) : "";
			final UUID uuid = UUID.fromString(from.getAttribute(Factory.UUID_ATTR));
			
			final Builder builder = Factory.createBuilder(name, uuid);
			final String aggression = from.getAttribute(Factory.AGGRESSION_ATTR);
			if (Factory.AGGRESSION_ATTR_VALUE_POSITIVE.equals(aggression)) {
				builder.setAggressionTrend(AggressionTrend.POSITIVE);
			}
			if (Factory.AGGRESSION_ATTR_VALUE_NEGATIVE.equals(aggression)) {
				builder.setAggressionTrend(AggressionTrend.NEGATIVE);
			}
			
			final NodeList dpNodes = from.getElementsByTagName(Factory.DATAPOINT_TAG);
			for (int i = 0; i < dpNodes.getLength(); i++) {
				final Element dpElement = (Element)dpNodes.item(i);
				double value = Double.parseDouble(dpElement.getAttribute(Factory.DATAPOINT_VALUE_ATTR));
				
				builder.addObservation(value);
			}
			
			return builder.build();
		}
	}
	
	private List<Double> sortedObservations = new ArrayList<>();
	private boolean reverse = false;
	
	private RawEmpiricalDistribution(String _name, UUID _uuid) {
		super(_name, _uuid);
	}

	@Override
	public Double getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new IllegalArgumentException(
					"Parameter passed to RawEmpiricalDistribution.getValue() must be in range [0, 1]");
		}
		final int binCount = sortedObservations.size();
		final double binLocation = (reverse ? (1 - t) : t) * binCount;
		final double result;
		
		if (binLocation < 0.5) {
			result = sortedObservations.get(0);
		} else if (binLocation > binCount - 0.5) {
			result = sortedObservations.get(binCount - 1);
		} else {
			// interpolate
			int leftBin = (int)Math.floor(binLocation - 0.5);
			int rightBin = leftBin + 1;
			double binT = binLocation - (leftBin + 0.5);
			
			final double leftValue = sortedObservations.get(leftBin);
			final Double rightValue = sortedObservations.get(rightBin);
			result = leftValue + binT * (rightValue - leftValue);
		}

		return result;
	} 
}
