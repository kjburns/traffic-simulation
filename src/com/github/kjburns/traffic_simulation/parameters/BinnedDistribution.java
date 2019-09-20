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
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.github.kjburns.traffic_simulation.parameters.EmpiricalDistribution.Factory.Builder;

/**
 * A distribution that conceptually resembles a histogram.
 * 
 * In order to work properly, the bins should butt up against each other. To ensure that this happens,
 * overlapping or gapped bins must be handled with assumptions.
 * <ul>
 *  <li>When processing the bins, the bins are first sorted according to minimum value.</li>
 * 	<li>If there are gaps between bins, bins with zero observations are added to fill the gaps.</li>
 *  <li>If a pair of bins partially overlaps, the bin on the right is truncated but its count
 *  remains the same*.</li>
 *  <li>If a pair of bins completely overlap, the bin on the inside is ignored*.</li>
 * </ul>
 * * The handling of these two situations is not logically consistent, but I can't think of a better
 * compromise. The best safeguard is to not define overlapping bins. 
 * @author Kevin J. Burns
 *
 */
class BinnedDistribution extends AbstractDistribution<Double>{
	private static class Bin {
		private static final String COUNT_ATTR = "count";
		private static final String MAX_VALUE_ATTR = "max-value";
		private static final String MIN_VALUE_ATTR = "min-value";
		private double minValue;
		private final double maxValue;
		private final int count;
		
		Bin(Element from) {
			minValue = Double.parseDouble(from.getAttribute(Bin.MIN_VALUE_ATTR));
			maxValue = Double.parseDouble(from.getAttribute(Bin.MAX_VALUE_ATTR));
			count = Integer.parseInt(from.getAttribute(Bin.COUNT_ATTR), 10);
		}

		public Bin(double min, double max, int ct) {
			minValue = min;
			maxValue = max;
			count = ct;
		}

		public final double getMinValue() {
			return this.minValue;
		}

		public final double getMaxValue() {
			return this.maxValue;
		}

		public final int getCount() {
			return this.count;
		}
		
		public final boolean containsSemiOpenInterval(double value) {
			return getMinValue() <= value && value < getMaxValue();
		}

		public void setMinValue(double value) {
			minValue = value;
		}
	}
	private static final String AGGRESSION_ATTR = "aggression";
	private static final String UUID_ATTR = "uuid";
	private static final String NAME_ATTR = "name";
	
	private Distribution<Double> backingDistr = null;
	private static final Comparator<Bin> BIN_SORTER = (a, b) -> {
		return Double.compare(a.getMinValue(), b.getMinValue());
	};

	public static BinnedDistribution fromXml(Element from) {
		final String name = from.hasAttribute(BinnedDistribution.NAME_ATTR) ? 
				from.getAttribute(BinnedDistribution.NAME_ATTR) : "";
		final UUID uuid = UUID.fromString(from.getAttribute(BinnedDistribution.UUID_ATTR));
		final AggressionTrend aggr = 
				AggressionTrend.valueOf(from.getAttribute(BinnedDistribution.AGGRESSION_ATTR).toUpperCase());
		
		BinnedDistribution ret = new BinnedDistribution(name, uuid);
		
		final NodeList binNodes = from.getElementsByTagName("bin");
		
		List<Bin> bins = generateInitialBinsList(from, binNodes);
		removeOverlaps(bins);
		bins.addAll(createNecessaryEmptyBins(bins));
		bins.sort(BIN_SORTER);
		
		ret.createBackingDistribution(bins, aggr);
		return ret;
	}
	
	private void createBackingDistribution(List<Bin> bins, AggressionTrend aggr) {
		final Builder builder = EmpiricalDistribution.Factory.createBuilder(getName(), getUuid());
		
		final int totalObservations = bins.stream().mapToInt((bin) -> {
			return bin.getCount();
		}).sum();
		if (totalObservations == 0) {
			throw new RuntimeException(
					"Binned distribution " + getUuid().toString() + " must have at least one observation.");
		}
		
		int runningTotal = 0;
		for (int i = 0; i < bins.size(); i++) {
			if (i == 0) {
				builder.addDataPoint(
						AggressionTrend.NEGATIVE.equals(aggr) ? 1. : 0., bins.get(0).getMinValue());
			}
			
			runningTotal += bins.get(i).getCount();
			double param = (double)runningTotal / totalObservations;
			if (AggressionTrend.NEGATIVE.equals(aggr)) {
				param = 1. - param;
			}
			builder.addDataPoint(param, bins.get(i).getMaxValue());
		}

		backingDistr = builder.build();
	}

	private static List<Bin> createNecessaryEmptyBins(List<Bin> bins) {
		List<Bin> emptyBins = new ArrayList<>();
		IntStream.range(0, bins.size() - 1).forEach((index) -> {
			final Bin current = bins.get(index);
			final Bin next = bins.get(index + 1);
			
			if (current.getMaxValue() < next.getMinValue()) {
				emptyBins.add(new Bin(current.getMaxValue(), next.getMinValue(), 0));
			}
		});
		
		return emptyBins;
	}

	private static void removeOverlaps(List<Bin> bins) {
		Bin binOnLeft = null;
		final Iterator<Bin> it = bins.iterator();
		while (it.hasNext()) {
			boolean shouldChangeBinOnLeft = true;
			final Bin currentBin = it.next();
			if (binOnLeft != null && binOnLeft.containsSemiOpenInterval(currentBin.getMinValue())) {
				// overlap!
				if (binOnLeft.containsSemiOpenInterval(currentBin.getMaxValue())) {
					// complete overlap
					it.remove();
					shouldChangeBinOnLeft = false;
				} else {
					// partial overlap
					currentBin.setMinValue(binOnLeft.getMaxValue());
				}
			}
			
			if (shouldChangeBinOnLeft) {
				binOnLeft = currentBin;
			}
		}
	}
	
	private static List<Bin> generateInitialBinsList(Element parentNode, final NodeList binNodes) {
		return IntStream.range(0, binNodes.getLength()).filter((index) -> {
			return binNodes.item(index).getParentNode() == parentNode;
		}).mapToObj((index) -> {
			return new Bin((Element)binNodes.item(index));
		}).sorted(BIN_SORTER).collect(Collectors.toList());
	}
	/*
	 * This class builds an EmpiricalDistribution in the background and uses
	 * that for all the math.
	 */
	protected BinnedDistribution(String _name, UUID _uuid) {
		super(_name, _uuid);
	}

	@Override
	public Double getValue(double t) {
		return backingDistr.getValue(t);
	}
}
