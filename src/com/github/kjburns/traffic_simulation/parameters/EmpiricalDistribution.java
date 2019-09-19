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
import java.util.Comparator;
import java.util.List;
import java.util.UUID;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

final class EmpiricalDistribution extends AbstractDistribution<Double> {
	private static class DataPoint {
		private final double parameter;
		private final double value;
		
		DataPoint(double param, double val) {
			checkParameter(param);
			
			parameter = param;
			value = val;
		}

		private void checkParameter(double param) {
			if (param < 0. || param > 1.) { 
				throw new RuntimeException("Empirical distribution: data point parameter must be in range [0, 1]. "
						+ "Attempted value was " + param);
			}
		}

		public final double getParameter() {
			return this.parameter;
		}

		public final double getValue() {
			return this.value;
		}
	}
	
	public static class Factory {
		private static final String DATAPOINT_VALUE_ATTR = "val";
		private static final String DATAPOINT_PROB_ATTR = "prob";
		private static final String UUID_ATTR = "uuid";
		private static final String NAME_ATTR = "name";

		public static class Builder {
			private final String name;
			private final UUID uuid;
			private final List<DataPoint> datapoints = new ArrayList<>();
			
			private Builder(String _name, UUID _uuid) {
				name = _name;
				uuid = _uuid;
			}
			
			public void addDataPoint(double param, double value) {
				datapoints.add(new DataPoint(param, value));
			}
			
			public Distribution<Double> build() {
				Comparator<DataPoint> comparator = (x, y) -> {
					return Double.compare(x.getParameter(), y.getParameter());
				};
				Collections.sort(datapoints, comparator);
				
				final DataPoint firstPoint = datapoints.get(0);
				if (firstPoint.getParameter() > 0.) {
					final DataPoint newFirstPoint = new DataPoint(0., firstPoint.getValue());
					datapoints.add(0, newFirstPoint);
				}
				
				final DataPoint lastPoint = datapoints.get(datapoints.size() - 1);
				if (lastPoint.getParameter() < 1.) {
					final DataPoint newLastPoint = new DataPoint(1., lastPoint.getValue());
					datapoints.add(newLastPoint);
				}
				
				EmpiricalDistribution ret = new EmpiricalDistribution(name, uuid);
				ret.sortedDataPoints.addAll(datapoints);
				
				return ret;
			}
		}
		
		public static Builder createBuilder(String _name, UUID _uuid) {
			return new Builder(_name, _uuid);
		}
		
		public static Distribution<Double> fromXml(Element from) {
			final String name = from.hasAttribute(Factory.NAME_ATTR) ? from.getAttribute(Factory.NAME_ATTR) : "";
			final UUID uuid = UUID.fromString(from.getAttribute(Factory.UUID_ATTR));
			
			final Builder builder = Factory.createBuilder(name, uuid);
			final NodeList dataPointNodes = from.getElementsByTagName("dp");
			
			for (int i = 0; i < dataPointNodes.getLength(); i++) {
				Element dp = (Element)dataPointNodes.item(i);
				
				final double prob = Double.parseDouble(dp.getAttribute(Factory.DATAPOINT_PROB_ATTR));
				final double val = Double.parseDouble(dp.getAttribute(Factory.DATAPOINT_VALUE_ATTR));
				
				builder.addDataPoint(prob, val);
			}
			
			return builder.build();
		}
	}
	
	private final List<DataPoint> sortedDataPoints = new ArrayList<>();
	
	private EmpiricalDistribution(String _name, UUID _uuid) {
		super(_name, _uuid);
	}

	@Override
	public Double getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new RuntimeException("Value of EmpiricalDistribution only defined on the domain [0, 1].");
		}
		final int intNr = getIntervalNumber(t);
		
		return interpolateOnInterval(intNr, t);
	}

	private double interpolateOnInterval(int intNr, double t) {
		final DataPoint lowDataPoint = sortedDataPoints.get(intNr);
		final DataPoint highDataPoint = sortedDataPoints.get(intNr + 1);

		final double lowParameter = lowDataPoint.getParameter();
		final double highParameter = highDataPoint.getParameter();

		final double lowValue = lowDataPoint.getValue();
		final double highValue = highDataPoint.getValue();
		
		final double fractionOfInterval = (lowParameter == highParameter) ? 
				0.5 : // in case there is a vertical line in the distribution and t falls on that line
				(t - lowParameter) / (highParameter - lowParameter);
		
		return lowValue + fractionOfInterval * (highValue - lowValue);
	}

	private int getIntervalNumber(double t) {
		/*
		 * via binary search
		 */
		final int intervalCount = sortedDataPoints.size() - 1;
		
		int left = 0;
		int right = intervalCount;
		int mid;
		
		while (left <= right) {
			mid = (left + right) / 2; // intentional integer division
			
			if (t > sortedDataPoints.get(mid + 1).getParameter()) {
				left = mid + 1;
			} else if (t < sortedDataPoints.get(mid).getParameter()) {
				right = mid;
			} else {
				return mid;
			}
		}
		
		/*
		 * This shouldn't happen
		 */
		return -1;
	}
}
