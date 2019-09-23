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

import java.awt.Color;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class ColorDistribution extends AbstractDistribution<Color> {
	private static final String SHARE_VALUE_ATTR = "value";
	private static final String SHARE_OCCURENCE_ATTR = "occurence";
	private static final String SHARE_TAG = "share";
	private static final String UUID_NAME = "uuid";
	private static final String NAME_ATTR = "name";

	private static class ColorBin {
		private final double startParameter;
		private double endParameter;
		private final Color value;
		
		private ColorBin(double startParameter, double endParameter, Color value) {
			this.startParameter = startParameter;
			this.endParameter = endParameter;
			this.value = value;
		}
		
		public boolean containsParameter(double t) {
			return (startParameter <= t && t <= endParameter);
		}

		public final Color getValue() {
			return this.value;
		}

		public void setEndParameterToOne() {
			endParameter = 1.;
		}
	}

	public static class Share {
		private final double occurence;
		private final Color value;
		
		public Share(double occurence, Color value) {
			this.occurence = occurence;
			this.value = value;
		}

		public final double getOccurence() {
			return this.occurence;
		}

		public final Color getValue() {
			return this.value;
		}
	}

	public static class Builder {
		private final List<Share> shares = new ArrayList<>();
		private final String name;
		private final UUID uuid;
		
		private Builder(String _name, UUID _uuid) {
			name = _name;
			uuid = _uuid;
		}
		
		public void addShare(double occurence, Color color) {
			shares.add(new Share(occurence, color));
		}
		
		public ColorDistribution build() {
			ColorDistribution ret = new ColorDistribution(name, uuid);
			
			final double sharesTotal = shares.stream().mapToDouble(Share::getOccurence).sum();
			if (sharesTotal <= 0.) {
				throw new RuntimeException("Sum of all shares must be greater than zero.");
			}
			
			final Comparator<? super Share> sorter = (a, b) -> {
				return Integer.compare(a.getValue().getRGB(), b.getValue().getRGB());
			};
			
			Collections.sort(shares, sorter);
			double acc = 0.;
			for (Share share : shares) {
				final double start = acc / sharesTotal;
				final double end = acc + share.getOccurence() / sharesTotal; 
				ret.sortedBins.add(new ColorBin(start, end, share.getValue()));
				
				acc = end;
			}
			
			ret.sortedBins.get(ret.sortedBins.size() - 1).setEndParameterToOne();
			
			return ret;
		}
	}
	
	public static Builder createBuilder(String name, UUID uuid) {
		return new Builder(name, uuid);
	}
	
	public static ColorDistribution fromXml(Element from) {
		final String name = from.hasAttribute(NAME_ATTR) ? from.getAttribute(NAME_ATTR) : "";
		final UUID uuid = UUID.fromString(from.getAttribute(UUID_NAME));
		
		final Builder builder = createBuilder(name, uuid);
		final NodeList shareNodes = from.getElementsByTagName(SHARE_TAG);
		IntStream.range(0, shareNodes.getLength()).filter((index) -> {
			return shareNodes.item(index).getParentNode() == from;
		}).forEach((index) -> {
			final Element share = (Element)shareNodes.item(index);
			final double occurence = Double.parseDouble(share.getAttribute(SHARE_OCCURENCE_ATTR));
			final Color color = Color.decode(share.getAttribute(SHARE_VALUE_ATTR));
			
			builder.addShare(occurence, color);
		});
		
		return builder.build();
	}

	private List<ColorBin> sortedBins = new ArrayList<>();
	
	protected ColorDistribution(String _name, UUID _uuid) {
		super(_name, _uuid);
	}
	
	@Override
	public Color getValue(double t) {
		if (t < 0. || t > 1.) {
			throw new IllegalArgumentException(
					"Color distribution getValue() requires parameter in range [0, 1]");
		}

		for (ColorBin bin : sortedBins) {
			if (bin.containsParameter(t)) {
				return bin.getValue();
			}
		}
		
		// this should never happen
		return null;
	}
}
