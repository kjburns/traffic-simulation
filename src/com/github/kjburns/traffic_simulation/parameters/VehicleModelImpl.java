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
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;

import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.github.kjburns.traffic_simulation.main.UnitsEnum;

class VehicleModelImpl implements VehicleModel {
	public static final String TAG = "vehicle-model";
	private static final String ARTICULATION_POINT_ATTR = "articulation-point";
	private static final String NAME_ATTR = "name";
	private static final String WIDTH_ATTR = "width";
	private static final String LENGTH_ATTR = "length";
	private static final String UUID_ATTR = "uuid";

	private class VehicleUnitImpl implements VehicleUnit {
		private Trailer trailer = null;
		private String name = "";
		private final double width;
		private final double length;
		private double articulationDistanceFromFront = Double.NaN;
		
		VehicleUnitImpl(double width, double length) {
			this.width = width;
			this.length = length;
		}
		
		VehicleUnitImpl(Element from, UnitsEnum units) {
			length = units.toMetres(Double.parseDouble(from.getAttribute(VehicleModelImpl.LENGTH_ATTR)));
			width = units.toMetres(Double.parseDouble(from.getAttribute(VehicleModelImpl.WIDTH_ATTR)));
			setName(from.hasAttribute(NAME_ATTR) ? 
					from.getAttribute(VehicleModelImpl.NAME_ATTR) : 
					"Vehicle Model " + uuid.toString());
			if (from.hasAttribute(VehicleModelImpl.ARTICULATION_POINT_ATTR)) {
				setArticulationDistanceFromFront(units.toMetres(
						Double.parseDouble(from.getAttribute(ARTICULATION_POINT_ATTR))));
			}
			
			final NodeList trailerElements = from.getElementsByTagName(TrailerImpl.XML_TAG);
			for (int i = 0; i < trailerElements.getLength(); i++) {
				Element tr = (Element)trailerElements.item(i);
				if (tr.getParentNode() == from) {
					setTrailer(new TrailerImpl(tr, units));
					break; // no need to keep going, there can only be one trailer attached to the lead veh
				}
			}
		}

		@Override
		public boolean hasTrailer() {
			return trailer != null;
		}

		@Override
		public Trailer getTrailer_rNull() {
			return trailer;
		}
		
		private void setTrailer(Trailer tr) {
			trailer = tr;
		}

		@Override
		public String getName() {
			return name;
		}
		
		private void setName(String _name) {
			name = _name;
		}

		@Override
		public double getWidth() {
			return width;
		}

		@Override
		public double getLength() {
			return length;
		}

		@Override
		public double getArticulationDistanceFromFront() {
			return Double.isNaN(articulationDistanceFromFront) ? 
					getLength() : 
					articulationDistanceFromFront;
		}
		
		private void setArticulationDistanceFromFront(double dist) {
			articulationDistanceFromFront = dist;
		}
	}

	private class TrailerImpl extends VehicleUnitImpl 
			implements Trailer {
		private static final String TOWING_POINT_ATTR = "towing-point";
		public static final String XML_TAG = "trailer";
		private final double towingDistanceFromFront;
		
		protected TrailerImpl(double width, double length, double _towingDistanceFromFront) {
			super(width, length);
			
			this.towingDistanceFromFront = _towingDistanceFromFront;
		}

		public TrailerImpl(Element from, UnitsEnum units) {
			super(from, units);
			
			towingDistanceFromFront = units.toMetres(
					Double.parseDouble(from.getAttribute(TrailerImpl.TOWING_POINT_ATTR)));
		}

		@Override
		public double getTowingDistanceFromFront() {
			return towingDistanceFromFront;
		}
	}
	
	private final VehicleUnitImpl leadVehicle;
	private final UUID uuid;
	
	public VehicleModelImpl(Element from, UnitsEnum fileUnits) {
		uuid = UUID.fromString(from.getAttribute(VehicleModelImpl.UUID_ATTR));
		leadVehicle = new VehicleUnitImpl(from, fileUnits);
	}
	
	private List<Trailer> getTrailersAsList() {
		List<Trailer> ret = new ArrayList<>();
		VehicleUnit currVehicle = getLeadVehicle();
		
		while (currVehicle.hasTrailer()) {
			Trailer trl = currVehicle.getTrailer_rNull();
			ret.add(trl);
			currVehicle = trl;
		}
		
		return ret;
	}
	
	private List<VehicleUnit> getAllVehiclesAsList() {
		List<VehicleUnit> ret = new ArrayList<>();
		ret.add(getLeadVehicle());
		ret.addAll(getTrailersAsList());
		
		return ret;
	}
	
	@Override
	public double getTotalLength() {
		double sum = getLeadVehicle().getLength();
		
		VehicleUnit towing = getLeadVehicle();
		Trailer towed;
		while (towing.hasTrailer()) {
			// modify towing vehicle length to account for distance from articulation point to back
			sum -= towing.getLength();
			sum += towing.getArticulationDistanceFromFront();
			
			towed = towing.getTrailer_rNull();
			// add towed vehicle length from towing point
			sum += towed.getLength() - towed.getTowingDistanceFromFront();
			
			towing = towed;
		}

		return sum;
	}

	@Override
	public double getMaximumWidth() {
		return getAllVehiclesAsList().stream().mapToDouble((vu) -> {
			return vu.getWidth();
		}).max().getAsDouble();
	}

	@Override
	public String getName() {
		return getLeadVehicle().getName();
	}

	@Override
	public UUID getUuid() {
		return uuid;
	}

	@Override
	public VehicleUnit getLeadVehicle() {
		return leadVehicle;
	}

	@Override
	public double getDistanceFromFront(VehicleUnit unit) {
		final List<VehicleUnit> units = getAllVehiclesAsList();
		final int unitIndex = units.indexOf(unit);
		
		double dist = units.stream().limit(unitIndex).mapToDouble((u) -> {
			double equivalentLength = u.getArticulationDistanceFromFront();
			if (u instanceof Trailer) {
				equivalentLength -= ((Trailer)u).getTowingDistanceFromFront();
			}
			
			return equivalentLength;
		}).sum();
		if (unit instanceof Trailer) {
			dist -= ((Trailer)unit).getTowingDistanceFromFront();
		}

		return dist;
	}

	@Override
	public Stream<VehicleUnit> unitsStream() {
		return getAllVehiclesAsList().stream();
	}

	@Override
	public Iterator<VehicleUnit> unitsIterator() {
		return getAllVehiclesAsList().iterator();
	}
}
