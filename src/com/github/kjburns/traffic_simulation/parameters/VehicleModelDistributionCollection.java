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

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class VehicleModelDistributionCollection implements DistributionCollection<VehicleModel>{
	public static final String DISTRIBUTION_TYPE_VALUE = "vehicle-models";
	private Map<UUID, Distribution<VehicleModel>> data = new HashMap<>();
	
	VehicleModelDistributionCollection(Element from, VehicleModelCollection models) {
		final NodeList distrElements = from.getElementsByTagName("distribution");
		
		for (int i = 0; i < distrElements.getLength(); i++) {
			Element e = (Element)distrElements.item(i);
			
			if (e.getParentNode() != from) {
				continue;
			}
			
			final VehicleModelDistribution distr = new VehicleModelDistribution(e, models);
			data.put(distr.getUuid(), distr);
		}
	}
	@Override
	public Distribution<VehicleModel> getByUuid(UUID id) {
		return data.get(id);
	}

	@Override
	public Iterator<Distribution<VehicleModel>> iterator() {
		return data.values().iterator();
	}

	@Override
	public Stream<Distribution<VehicleModel>> stream() {
		return data.values().stream();
	}
}
