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

import java.util.UUID;
import java.util.stream.IntStream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class VehicleModelDistribution extends ThingDistribution<VehicleModel> {
	private static final String SHARE_VALUE_ATTR = "value";
	private static final String SHARE_OCCURENCE_ATTR = "occurence";
	private static final String SHARE_TAG = "share";
	private static final String UUID_ATTR = "uuid";
	private static final String NAME_ATTR = "name";
	private final String name;
	private final UUID uuid;
	
	public VehicleModelDistribution(Element from, VehicleModelCollection models) {
		name = from.hasAttribute(VehicleModelDistribution.NAME_ATTR) ?
			from.getAttribute(NAME_ATTR) : "";
		uuid = UUID.fromString(from.getAttribute(VehicleModelDistribution.UUID_ATTR));
		
		final NodeList shareElements = from.getElementsByTagName(VehicleModelDistribution.SHARE_TAG);
		IntStream.range(0, shareElements.getLength()).filter((index) -> {
			return shareElements.item(index).getParentNode() == from;
		}).forEach((index) -> {
			Element e = (Element)shareElements.item(index);
			double amt = Double.parseDouble(e.getAttribute(VehicleModelDistribution.SHARE_OCCURENCE_ATTR));
			UUID vehUuid = UUID.fromString(e.getAttribute(VehicleModelDistribution.SHARE_VALUE_ATTR));
			
			final VehicleModel model = models.getByUuid(vehUuid);
			if (model == null) {
				throw new RuntimeException(
						"Vehicle model " + vehUuid.toString() + 
						" not found, but specified in distribution " + name);
			}
			addShare(amt, model);
		});
	}
	
	@Override
	public String getName() {
		return name;
	}

	@Override
	public UUID getUuid() {
		return uuid;
	}
}
