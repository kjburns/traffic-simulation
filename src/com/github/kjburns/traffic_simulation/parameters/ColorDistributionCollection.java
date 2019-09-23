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
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class ColorDistributionCollection implements DistributionCollection<Color>{
	public static final String DISTRIBUTION_TYPE_VALUE = "colors";
	final private Map<UUID, Distribution<Color>> data = new HashMap<>();
	
	public ColorDistributionCollection(Element from) {
		final NodeList distrElements = from.getElementsByTagName(ColorDistribution.TAG);
		
		data.putAll(IntStream.range(0, distrElements.getLength()).filter((index) -> {
			return distrElements.item(index).getParentNode() == from;
		}).mapToObj((index) -> {
			Element e = (Element)distrElements.item(index);
			return ColorDistribution.fromXml(e);
		}).collect(
				Collectors.toMap(
						ColorDistribution::getUuid, 
						Function.identity()
				)
		));
	}
	
	@Override
	public Distribution<Color> getByUuid(UUID id) {
		return data.get(id);
	}

	@Override
	public Iterator<Distribution<Color>> iterator() {
		return data.values().iterator();
	}

	@Override
	public Stream<Distribution<Color>> stream() {
		return data.values().stream();
	}
}
