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

import com.github.kjburns.traffic_simulation.main.UnitsEnum;

class VehicleModelCollectionImpl 
		implements VehicleModelCollection {
	public static final String COLLECTION_TYPE = "vehicle-models";
	
	private Map<UUID, VehicleModel> data = new HashMap<>();
	
	VehicleModelCollectionImpl(Element from) {
		final String versionStr = from.getAttribute("version");
		final int version = Integer.parseInt(versionStr, 10);
		
		if (version == 1) {
			readFileVersion1(from);
		}
	}

	private void readFileVersion1(Element from) {
		final String unitsAttr = "units";
		final String unitsStr = from.getAttribute(unitsAttr);
		final UnitsEnum units = UnitsEnum.valueOf(unitsStr.toUpperCase());
		
		final NodeList modelElements = from.getElementsByTagName(VehicleModelImpl.TAG);
		for (int i = 0; i < modelElements.getLength(); i++) {
			final Element element = (Element)modelElements.item(i);
			if (element.getParentNode() != from) {
				continue;
			}
			
			final VehicleModelImpl model = new VehicleModelImpl(element, units);
			data.put(model.getUuid(), model);
		}
	}

	@Override
	public VehicleModel getByUuid(UUID id) {
		return data.get(id);
	}

	@Override
	public Iterator<VehicleModel> iterator() {
		return data.values().iterator();
	}

	@Override
	public Stream<VehicleModel> stream() {
		return data.values().stream();
	}
}
